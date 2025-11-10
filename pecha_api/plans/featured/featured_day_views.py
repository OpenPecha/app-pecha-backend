from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from .featured_day_service import get_featured_day_service


oauth2_scheme = HTTPBearer()
user_follow_router = APIRouter(
    prefix="/plans/featured",
    tags=["Featured Plans"]
)


@user_follow_router.get("/day", status_code=status.HTTP_200_OK)
def get_featured_day():
    return get_featured_day_service()

