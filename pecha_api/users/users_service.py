import io
import logging

from fastapi import HTTPException, status, UploadFile
from jwt import ExpiredSignatureError
from starlette.responses import JSONResponse

from .user_response_models import UserInfoRequest, UserInfoResponse, SocialMediaProfile
from .users_enums import SocialProfile
from .users_models import Users
from ..auth.auth_repository import decode_token
from .users_repository import get_user_by_email, update_user
from ..uploads.S3_utils import delete_file, upload_bytes, generate_presigned_upload_url
from ..db.database import SessionLocal
from ..config import get, get_int
from PIL import Image


def get_user_info(token: str):
    try:
        current_user = validate_and_extract_user_details(token=token)
        user_info_response = generate_user_info_response(user=current_user)
        return user_info_response
    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code,
                            content={"message": exception.detail})


def generate_user_info_response(user: Users):
    if user:
        social_media_profiles = []
        for account in user.social_media_accounts:
            social_media_profile = SocialMediaProfile(
                account=get_social_profile(value=account.platform_name),
                url=account.profile_url
            )
            social_media_profiles.append(social_media_profile)

        user_info_response = UserInfoResponse(
            firstname=user.firstname,
            lastname=user.lastname,
            username=user.username,
            email=user.email,
            title=user.title,
            organization=user.organization,
            educations=user.education.split(',') if user.education else [],
            avatar_url=user.avatar_url,
            about_me=user.about_me,
            followers=0,
            following=0,
            social_profiles=social_media_profiles
        )
        return user_info_response


def update_user_info(token: str, user_info_request: UserInfoRequest):
    try:
        current_user = validate_and_extract_user_details(token=token)
        if current_user:
            current_user.firstname = user_info_request.firstname
            current_user.lastname = user_info_request.lastname
            current_user.title = user_info_request.title
            current_user.organization = user_info_request.organization
            current_user.educations = ','.join(user_info_request.educations)
            current_user.avatar_url = user_info_request.avatar_url
            current_user.about_me = user_info_request.about_me
            current_user.social_profiles = user_info_request.social_profiles
            db_session = SessionLocal()
            update_user(db=db_session, user=current_user)

    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code,
                            content={"message": exception.detail})


def upload_user_image(token: str, file: UploadFile):
    try:
        user_info = validate_and_extract_user_details(token=token)
        # Validate and compress the uploaded image
        compressed_image = validate_and_compress_image(file)
        file_path = f'images/profile_images/{user_info.id}.jpg'
        delete_file(file_path=file_path)
        upload_key = upload_bytes(
            bucket_name=get("AWS_BUCKET_NAME"),
            s3_key=file_path,
            file=compressed_image,
            content_type=file.content_type
        )
        presigned_url = generate_presigned_upload_url(
            bucket_name=get("AWS_BUCKET_NAME"),
            s3_key=upload_key,
            content_type=file.content_type
        )
        return presigned_url
    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code,
                            content={"message": exception.detail})


def validate_and_extract_user_details(token: str) -> Users:
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        db_session = SessionLocal()
        user = get_user_by_email(db=db_session, email=email)
        return user
    except ExpiredSignatureError as exception:
        logging.debug("exception",exception)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_social_profile(value: str) -> SocialProfile:
    try:
        return SocialProfile(value.lower())
    except ValueError:
        raise ValueError(f"'{value}' is not a valid SocialProfile")


def validate_and_compress_image(file: UploadFile) -> io.BytesIO:
    max_file_size = get_int("MAX_FILE_SIZE_MB")
    MAX_FILE_SIZE_BYTES = max_file_size * 1024 * 1024
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed."
        )
    file.file.seek(0, 2)  # Move to the end of the file to get its size
    file_size = file.file.tell()
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {max_file_size} MB limit."
        )
    file.file.seek(0)  # Reset file pointer
    # Read and compress the image
    try:
        image = Image.open(file.file)
        compressed_image_io = io.BytesIO()
        image.save(compressed_image_io, format="JPEG", quality=get_int("COMPRESSED_QUALITY"))
        compressed_image_io.seek(0)
        return compressed_image_io
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process the image: {str(e)}"
        )
