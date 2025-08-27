from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...db import database
from .plan_auth_enum import PlanRegistrationSource
from .plan_auth_model import CreateAuthorRequest
from starlette import status


plan_auth_router = APIRouter(
    prefix="/plan-auth",
    tags=["Plan Authentications"],
)


@plan_auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(create_user_request: CreateAuthorRequest):
    registration_source = PlanRegistrationSource.EMAIL
    return register_author(
        create_user_request=create_user_request,
        registration_source=registration_source
    )