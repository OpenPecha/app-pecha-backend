from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from .featured_day_service import get_featured_day_service


oauth2_scheme = HTTPBearer()
user_follow_router = APIRouter(
    prefix="/plans",
    tags=["Featured Plans"]
)


@user_follow_router.get("/featured-day", status_code=status.HTTP_204_NO_CONTENT)
def get_featured_day():
    return get_featured_day_service()

