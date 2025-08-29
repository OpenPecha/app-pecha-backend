from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...db import database
from .plan_auth_enum import PlanRegistrationSource
from .plan_auth_model import CreateAuthorRequest
from starlette import status
from .plan_auth_services import register_author, verify_author_email


plan_auth_router = APIRouter(
    prefix="/plan-auth",
    tags=["Plan Authentications"],
)


@plan_auth_router.post("/register", status_code=status.HTTP_202_ACCEPTED)
def register_user(create_user_request: CreateAuthorRequest):
    return register_author(
        create_user_request=create_user_request
    )


@plan_auth_router.get("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(token: str = Query(..., description="Verification token")):
    return verify_author_email(token=token)