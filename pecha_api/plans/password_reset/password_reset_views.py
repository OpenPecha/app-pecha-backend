from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status
from ..password_reset.password_reset_services import request_reset_password, update_password
from .password_reset_models import PasswordResetRequest, ResetPasswordRequest
from typing import Annotated

oauth2_scheme = HTTPBearer()

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@auth_router.post("/plan-request-reset-password", status_code=status.HTTP_202_ACCEPTED)
async def password_reset_request(reset_request: PasswordResetRequest):
    request_reset_password(email=reset_request.email)


@auth_router.post("/plan-reset-password", status_code=status.HTTP_200_OK)
async def password_reset(reset_password_request: ResetPasswordRequest,
                   authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]):
    update_password(token=authentication_credential.credentials, password=reset_password_request.password)
