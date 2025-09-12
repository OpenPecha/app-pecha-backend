import os, uuid
from fastapi import UploadFile, HTTPException, status
from typing import Optional

import logging
from ...config import get, get_int
from ...image_utils import ImageUtils
from ...uploads.S3_utils import upload_bytes, generate_presigned_access_url
from ...plans.authors.plan_author_service import validate_and_extract_author_details
from .media_response_models import MediaUploadResponse
from ...plans.response_message import (
    IMAGE_UPLOAD_SUCCESS,
    UNEXPECTED_ERROR_UPLOAD,
    INVALID_FILE_FORMAT,
    FILE_TOO_LARGE
)

def validate_file(file: UploadFile) -> None:
    file_extension = os.path.splitext(file.filename.lower())[1] if file.filename else ''
    if file_extension not in get("ALLOWED_EXTENSIONS"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_FILE_FORMAT)
    
    if hasattr(file, 'size') and file.size and file.size > get_int("MAX_FILE_SIZE"):
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=FILE_TOO_LARGE)


def upload_media_file(token: str, plan_id: Optional[str], file: UploadFile, path: str = "images/plan_images") -> MediaUploadResponse:
    validate_and_extract_author_details(token=token)
    try:
        validate_file(file)
        
        image_utils = ImageUtils()
        compressed_image = image_utils.validate_and_compress_image(file=file, content_type=file.content_type)   
        file_name, ext = os.path.splitext(file.filename)
        unique_id = str(uuid.uuid4())

        image_path_full = f"{path}/{plan_id}/{unique_id}" if plan_id is not None else f"{path}/{unique_id}"
        plan_image_name = f"{image_path_full}/{file_name}{ext}"
        upload_key = upload_bytes(
            bucket_name=get("AWS_BUCKET_NAME"),
            s3_key=plan_image_name,
            file=compressed_image,
            content_type=file.content_type or 'image/jpeg'
        )
        
        presigned_url = generate_presigned_access_url(
            bucket_name=get("AWS_BUCKET_NAME"),
            s3_key=upload_key
        )
        
        return MediaUploadResponse(url=presigned_url, key=upload_key, path=image_path_full, message=IMAGE_UPLOAD_SUCCESS)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error during media upload: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=UNEXPECTED_ERROR_UPLOAD)
