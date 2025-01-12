from typing import List

from fastapi import HTTPException, status
from starlette.responses import JSONResponse

from .user_response_models import UserInfoRequest, UserInfoResponse, SocialMediaProfile
from .users_models import Users
from ..auth.auth_repository import decode_token
from .users_repository import get_user_by_email,save_user
from ..db.database import SessionLocal


def get_user_info(token: str):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        db_session = SessionLocal()
        user = get_user_by_email(db=db_session, email=email)
        user_info_response = generate_user_info_response(user=user)
        return user_info_response
    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code,
                            content={"message": exception.detail})


def generate_user_info_response(user: Users):
    if user:
        social_media_profiles = []
        for account in user.social_media_accounts:
            social_media_profile = SocialMediaProfile(
                account=account.platform_name,
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
        payload = decode_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        db_session = SessionLocal()
        user = get_user_by_email(db=db_session, email=email)
        if user:
            user.firstname = user_info_request.firstname
            user.lastname = user_info_request.lastname
            user.title = user_info_request.title
            user.organization = user_info_request.organization
            user.educations = ','.join(user_info_request.educations)
            user.avatar_url = user_info_request.avatar_url
            user.about_me = user_info_request.about_me
            user.social_profiles = user_info_request.social_profiles
            save_user(db=db_session,user=user)

    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code,
                            content={"message": exception.detail})
