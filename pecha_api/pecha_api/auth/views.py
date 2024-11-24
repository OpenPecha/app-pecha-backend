from fastapi import APIRouter
from ..db import database
from starlette import status
from .service import create_user, authenticate_and_generate_tokens,refresh_access_token
from .models import CreateUserRequest, UserLoginRequest

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


@auth_router.post("/login", status_code=status.HTTP_200_OK)
def login_user(user_login_request: UserLoginRequest):
   return  authenticate_and_generate_tokens(
       email=user_login_request.email,
       password= user_login_request.password
    )


@auth_router.post("/refresh-token", status_code=status.HTTP_200_OK)
def refresh_token(refresh_token: str):
    return refresh_access_token(refresh_token)

