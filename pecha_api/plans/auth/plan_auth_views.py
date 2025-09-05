from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .plan_auth_models import CreateAuthorRequest, AuthorDetails, AuthorVerificationResponse, AuthorLoginRequest, AuthorLoginResponse
from starlette import status
from .plan_auth_services import register_author, verify_author_email
from typing import Annotated
oauth2_scheme = HTTPBearer()
from .plan_auth_services import authenticate_and_generate_tokens

plan_auth_router = APIRouter(
    prefix="/cms/auth",
    tags=["Plan Authentications"],
)


@plan_auth_router.post("/register", status_code=status.HTTP_202_ACCEPTED,response_model=AuthorDetails)
def register_user(create_user_request: CreateAuthorRequest) -> AuthorDetails:
    return register_author(
        create_user_request=create_user_request
    )

@plan_auth_router.get("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]) -> AuthorVerificationResponse:
    return verify_author_email(token=authentication_credential.credentials)

@plan_auth_router.post("/login", status_code=status.HTTP_200_OK)
def login_user(author_login_request: AuthorLoginRequest) -> AuthorLoginResponse:
    return authenticate_and_generate_tokens(
        email=author_login_request.email,
        password=author_login_request.password
    )