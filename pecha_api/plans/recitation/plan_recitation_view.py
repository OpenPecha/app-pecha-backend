from fastapi import APIRouter
from fastapi.security import HTTPBearer
from starlette import status
from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from pecha_api.plans.recitation.plan_recitation_response_models import CreateRecitationRequest
from pecha_api.plans.recitation.plan_recitation_services import create_recitation

oauth2_scheme=HTTPBearer()
recitation_router=APIRouter(
    prefix="/plans",
    tags=["Recitation"],
)

@recitation_router.post("/recitation",status_code=status.HTTP_201_CREATED)
async def create_recitation(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
                            create_recitation_request: CreateRecitationRequest):
    return await create_recitation(
        token=authentication_credential.credentials,
        create_recitation_request=create_recitation_request
    )