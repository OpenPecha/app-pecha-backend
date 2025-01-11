from fastapi import APIRouter, Header, Depends
from starlette import status

from .user_response_models import UserInfoRequest
from ..db import database
from fastapi import HTTPException
from typing import Annotated
from .users_service import get_user_info, update_user_info

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


def get_token_from_header(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    return authorization.split(" ")[1]


@user_router.get("/info", status_code=status.HTTP_200_OK)
def get_user_information(token: Annotated[str, Depends(get_token_from_header)]):
    return get_user_info(token=token)

@user_router.post("/info", status_code=status.HTTP_201_CREATED)
def get_user_information(token: Annotated[str, Depends(get_token_from_header)], user_info_request: UserInfoRequest):
    return update_user_info(token=token,user_info_request=user_info_request)
