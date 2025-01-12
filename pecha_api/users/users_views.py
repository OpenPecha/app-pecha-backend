from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from .user_response_models import UserInfoRequest
from ..db import database
from typing import Annotated
from .users_service import get_user_info, update_user_info, upload_user_image

oauth2_scheme = HTTPBearer()
user_router = APIRouter(
    prefix="/users",
    tags=["User Profile"]
)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@user_router.get("/info", status_code=status.HTTP_200_OK)
def get_user_information(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]):
    return get_user_info(token=authentication_credential.credentials)


@user_router.post("/info", status_code=status.HTTP_201_CREATED)
def update_user_information(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
                            user_info_request: UserInfoRequest):
    return update_user_info(token=authentication_credential.credentials, user_info_request=user_info_request)


@user_router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_user_avatar_image(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
                             file: UploadFile = File(...)):
    return upload_user_image(token=authentication_credential.credentials, file=file)
