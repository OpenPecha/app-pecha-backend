from fastapi import HTTPException, status, UploadFile
from starlette.responses import JSONResponse

from .user_response_models import UserInfoRequest, UserInfoResponse, SocialMediaProfile
from .users_enums import SocialProfile
from .users_models import Users
from ..auth.auth_repository import decode_token
from .users_repository import get_user_by_email, save_user
from ..uploads.S3_utils import upload_file, delete_file
from ..db.database import SessionLocal
from ..config import get


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
            save_user(db=db_session, user=current_user)

    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code,
                            content={"message": exception.detail})


def upload_user_image(token: str, file: UploadFile):
    try:
        user_info = validate_and_extract_user_details(token=token)
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only image files are allowed.")
        file_path = f'images/profile_images/{user_info.id}.jpg'
        delete_file(file_path=file_path)
        upload_key = upload_file(
            bucket_name=get("AWS_BUCKET_NAME"),
            s3_key=file_path,
            file=file
        )
        return upload_key
    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code,
                            content={"message": exception.detail})


def validate_and_extract_user_details(token: str) -> Users:
    payload = decode_token(token)
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    db_session = SessionLocal()
    user = get_user_by_email(db=db_session, email=email)
    return user


def get_social_profile(value: str) -> SocialProfile:
    try:
        return SocialProfile(value.lower())
    except ValueError:
        raise ValueError(f"'{value}' is not a valid SocialProfile")
