import io
import logging
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

import jose
from fastapi import HTTPException, status, UploadFile
from jose import jwt, JWTError
from jose.exceptions import JWTClaimsError
from jwt import ExpiredSignatureError

from pecha_api.error_contants import ErrorConstants
from .user_response_models import UserInfoRequest, UserInfoResponse, SocialMediaProfile, PublisherInfoResponse
from .users_enums import SocialProfile
from .users_models import Users, SocialMediaAccount
from ..auth.auth_repository import verify_auth0_token, decode_backend_token
from .users_repository import get_user_by_email, update_user, get_user_by_username
from ..uploads.S3_utils import delete_file, upload_bytes, generate_presigned_upload_url
from ..db.database import SessionLocal
from ..config import get, get_int
from PIL import Image

from pecha_api.utils import Utils
from pecha_api.image_utils import ImageUtils


def get_user_info(token: str) -> UserInfoResponse:
    current_user = validate_and_extract_user_details(token=token)
    user_info_response = generate_user_info_response(user=current_user)
    return user_info_response

def fetch_user_by_email(email: str) -> Optional[UserInfoResponse]:
    with SessionLocal() as db_session:
        user = get_user_by_email(db=db_session, email=email)
        db_session.close()
    return generate_user_info_response(user=user)

def generate_user_info_response(user: Users) -> Optional[UserInfoResponse]:
    if user:
        social_media_profiles = []
        with SessionLocal() as db_session:
            db_session.add(user)
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
                location=user.location,
                educations=user.education.split(',') if user.education else [],
                avatar_url=generate_presigned_upload_url(bucket_name=get("AWS_BUCKET_NAME"), s3_key=user.avatar_url),
                about_me=user.about_me,
                followers=0,
                following=0,
                social_profiles=social_media_profiles
            )
            return user_info_response
    return None


def update_user_info(token: str, user_info_request: UserInfoRequest) -> Users:
    current_user = validate_and_extract_user_details(token=token)
    if current_user:
        current_user.firstname = user_info_request.firstname
        current_user.lastname = user_info_request.lastname
        current_user.title = user_info_request.title
        current_user.organization = user_info_request.organization
        current_user.location = user_info_request.location
        current_user.education = ','.join(user_info_request.educations)
        current_user.avatar_url = Utils.extract_s3_key(presigned_url=user_info_request.avatar_url)
        current_user.about_me = user_info_request.about_me
        with SessionLocal() as db_session:
            try:
                db_session.add(current_user)
                update_social_profiles(user=current_user,social_profiles=user_info_request.social_profiles)
                updated_user = update_user(db=db_session, user=current_user)
                return updated_user
            except Exception as e:
                db_session.rollback()
                logging.error(f"Failed to update user info: {e}")
                raise HTTPException(status_code=500, detail="Internal Server Error")


def update_social_profiles(user: Users, social_profiles: List[SocialMediaProfile]) -> None:
    existing_profiles = {profile.platform_name: profile for profile in user.social_media_accounts}

    for profile_data in social_profiles or []:
        platform = profile_data.account.name
        url = profile_data.url

        if platform in existing_profiles:
            # Update existing profile
            existing_profiles[platform].profile_url = url
        else:
            # Add new profile
            user.social_media_accounts.append(SocialMediaAccount(
                user_id=user.id,
                platform_name=platform,
                profile_url=url
            ))


def upload_user_image(token: str, file: UploadFile) -> str:
    current_user = validate_and_extract_user_details(token=token)
    # Validate and compress the uploaded image
    if current_user:
        image_utils = ImageUtils()
        compressed_image = image_utils.validate_and_compress_image(file=file, content_type=file.content_type)
        file_path = f'images/profile_images/{current_user.id}.jpg'
        delete_file(file_path=file_path)
        upload_key = upload_bytes(
            bucket_name=get("AWS_BUCKET_NAME"),
            s3_key=file_path,
            file=compressed_image,
            content_type=file.content_type
        )
        presigned_url = generate_presigned_upload_url(
            bucket_name=get("AWS_BUCKET_NAME"),
            s3_key=upload_key
        )
        current_user.avatar_url = Utils.extract_s3_key(presigned_url=presigned_url)
        with SessionLocal() as db_session:
            update_user(db=db_session, user=current_user)
            return presigned_url


def validate_and_extract_user_details(token: str) -> Users:
    try:
        payload = validate_token(token)
        email = payload.get("email")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
        with SessionLocal() as db_session:
            user = get_user_by_email(db=db_session, email=email)
            return user
    except ExpiredSignatureError as exception:
        logging.debug(f"exception: {exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
    except jose.ExpiredSignatureError as exception:
        logging.debug(f"exception: {exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
    except JWTClaimsError as exception:
        logging.debug(f"exception: {exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
    except ValueError as value_exception:
        logging.debug(f"exception: {value_exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
    except JWTError as jwt_exception:
        logging.debug(f"exception: {jwt_exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)

def verify_admin_access(token: str) -> bool:
    current_user = validate_and_extract_user_details(token=token)
    if hasattr(current_user, 'is_admin') and current_user.is_admin is not None:
        return current_user.is_admin
    else:
        return False

def validate_user_exists(token: str) -> bool:
    current_user = validate_and_extract_user_details(token=token)
    if current_user:
        return True
    else:
        return False


def get_social_profile(value: str) -> SocialProfile:
    try:
        return SocialProfile(value.lower().replace("_","."))
    except ValueError:
        raise ValueError(f"'{value}' is not a valid SocialProfile")

def validate_token(token: str) -> Dict[str, Any]:
    if get("DOMAIN_NAME") in jwt.get_unverified_claims(token=token)["iss"]:
        return verify_auth0_token(token)
    else:
        return decode_backend_token(token)


def get_publisher_info_by_username(username: str) -> Optional[PublisherInfoResponse]:
   
    try:
        with SessionLocal() as db_session:
            user = get_user_by_username(db=db_session, username=username)
            if user:
                avatar_url = None
                if user.avatar_url:
                    avatar_url = generate_presigned_upload_url(
                        bucket_name=get("AWS_BUCKET_NAME"), 
                        s3_key=user.avatar_url
                    )
                
                return PublisherInfoResponse(
                    id=str(user.id),
                    username=user.username,
                    firstname=user.firstname,
                    lastname=user.lastname,
                    avatar_url=avatar_url
                )
    except Exception as e:
        logging.error(f"Error getting publisher info by username: {e}")
    return None
