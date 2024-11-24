from fastapi import APIRouter
from ..db import database
from starlette import status
from .service import create_user
from .models import CreateUserRequest

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentications"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(create_user_request: CreateUserRequest):
    return create_user(create_user_request)

