from fastapi import APIRouter
from ..db import database
from starlette import status
from .auth_service import authenticate_and_generate_tokens, refresh_access_token, register_user_with_source
from .auth_models import CreateUserRequest, UserLoginRequest, RefreshTokenRequest
from .auth_enums import RegistrationSource

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
    return register_user_with_source(
        create_user_request=create_user_request,
        registration_source=RegistrationSource.EMAIL
    )


@auth_router.post("/login", status_code=status.HTTP_200_OK)
def login_user(user_login_request: UserLoginRequest):
    return authenticate_and_generate_tokens(
        email=user_login_request.email,
        password=user_login_request.password
    )


@auth_router.post("/refresh-token", status_code=status.HTTP_200_OK)
def refresh_token(refresh_token_request: RefreshTokenRequest):
    return refresh_access_token(refresh_token_request.token)
