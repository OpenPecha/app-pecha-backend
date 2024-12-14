from fastapi import APIRouter
from starlette import status
user_router = APIRouter(
    prefix="/users",
    tags=["User Profile"]
)

