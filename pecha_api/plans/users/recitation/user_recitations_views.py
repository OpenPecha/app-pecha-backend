from fastapi import APIRouter, Depends
from starlette import status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated

from pecha_api.plans.users.recitation.user_recitations_response_models import (
    CreateUserRecitationRequest,
    UserRecitationsResponse
)
from pecha_api.plans.users.recitation.user_recitations_services import (
    create_user_recitation_service,
    get_user_recitations_service
)

oauth2_scheme = HTTPBearer()
user_recitation_router = APIRouter(
    prefix="/users/me",
    tags=["User Recitations"]
)

@user_recitation_router.post("/recitations",status_code=status.HTTP_200_OK)
async def create_user_recitation(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],  create_user_recitation_request: CreateUserRecitationRequest):
    return await create_user_recitation_service(
        token=authentication_credential.credentials,
        create_user_recitation_request=create_user_recitation_request
    )

@user_recitation_router.get("/recitations", status_code=status.HTTP_200_OK, response_model=UserRecitationsResponse)
async def get_user_recitations(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]):
    return await get_user_recitations_service(token=authentication_credential.credentials)