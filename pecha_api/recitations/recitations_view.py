from fastapi import APIRouter
from starlette import status
from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials , HTTPBearer
from pecha_api.recitations.recitations_response_models import CreateRecitationsRequest
from pecha_api.recitations.recitations_services import create_recitations_service

oauth2_scheme=HTTPBearer()
recitation_router=APIRouter(
    prefix="/recitations",
    tags=["Recitations"],
)

@recitation_router.post("",status_code=status.HTTP_204_NO_CONTENT)
async def create_recitations(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
                            create_recitations_request: CreateRecitationsRequest):
    return await create_recitations_service(
        token=authentication_credential.credentials,
        create_recitations_request=create_recitations_request
    )