from fastapi import APIRouter, Query

from .plan_auth_model import CreateAuthorRequest, AuthorResponse, AuthorLoginRequest, AuthorLoginResponse
from starlette import status
from .plan_auth_services import register_author, verify_author_email
from .plan_auth_services import authenticate_and_generate_tokens

plan_auth_router = APIRouter(
    prefix="/plan-auth",
    tags=["Plan Authentications"],
)


@plan_auth_router.post("/register", status_code=status.HTTP_202_ACCEPTED)
def register_user(create_user_request: CreateAuthorRequest) -> AuthorResponse:
    return register_author(
        create_user_request=create_user_request
    )

@plan_auth_router.get("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(token: str = Query(..., description="Verification token")):
    return verify_author_email(token=token)

@plan_auth_router.post("/login", status_code=status.HTTP_200_OK)
def login_user(author_login_request: AuthorLoginRequest) -> AuthorLoginResponse:
    return authenticate_and_generate_tokens(
        email=author_login_request.email,
        password=author_login_request.password
    )