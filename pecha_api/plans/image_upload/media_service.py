import os, uuid
from fastapi import UploadFile, HTTPException, status
import logging
from ...config import get
from ...image_utils import ImageUtils
from ...uploads.S3_utils import upload_bytes, generate_presigned_access_url
from .media_response_models import MediaUploadResponse


ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes


def validate_file(file: UploadFile) -> None:
    file_extension = os.path.splitext(file.filename.lower())[1] if file.filename else ''
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_file",
                "message": "Only JPEG, PNG, and WebP images are allowed. Maximum size: 5MB"
            }
        )
    
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "file_too_large", 
                "message": "File size exceeds 5MB limit"
            }
        )


def upload_media_file(file: UploadFile, path: str) -> MediaUploadResponse:
    try:
        validate_file(file)
        
        image_utils = ImageUtils()
        compressed_image = image_utils.validate_and_compress_image(
            file=file, 
            content_type=file.content_type
        )
        
        if not path.endswith('/'):
            path += '/'
            
        file_extension = os.path.splitext(file.filename.lower())[1] if file.filename else '.jpg'
        if file_extension not in ALLOWED_EXTENSIONS:
            file_extension = '.jpg'
            
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        s3_key = f"{path}{unique_filename}"
        
        upload_key = upload_bytes(
            bucket_name=get("AWS_BUCKET_NAME"),
            s3_key=s3_key,
            file=compressed_image,
            content_type=file.content_type or 'image/jpeg'
        )
        
        presigned_url = generate_presigned_access_url(
            bucket_name=get("AWS_BUCKET_NAME"),
            s3_key=upload_key
        )
        
        return MediaUploadResponse(
            url=presigned_url,
            message="Image uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error during media upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "upload_failed",
                "message": "An unexpected error occurred during upload"
            }
        )
