from fastapi import APIRouter, Depends
from starlette import status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated

from pecha_api.plans.users.recitation.plan_user_recitation_response_models import CreateUserRecitationRequest
from pecha_api.plans.users.recitation.plan_user_recitation_services import create_user_recitation_service

oauth2_scheme = HTTPBearer()
user_recitation_router = APIRouter(
    prefix="/users/me",
    tags=["User Recitations"]
)

@user_recitation_router.post("/recitations",status_code=status.HTTP_204_NO_CONTENT)
def create_user_recitation(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],  create_user_recitation_request: CreateUserRecitationRequest):
    return create_user_recitation_service(
        token=authentication_credential.credentials,
        create_user_recitation_request=create_user_recitation_request
    )