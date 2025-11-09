from fastapi import APIRouter, Query
from starlette import status
from typing import Annotated, List
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials , HTTPBearer
from pecha_api.plans.recitation.plan_recitation_response_models import CreateRecitationRequest, RecitationsResponse
from pecha_api.plans.recitation.plan_recitation_services import create_recitation_service, get_list_of_recitations_service

oauth2_scheme=HTTPBearer()
recitation_router=APIRouter(
    prefix="/plans/recitation",
    tags=["Recitation"],
)

@recitation_router.post("",status_code=status.HTTP_204_NO_CONTENT)
async def create_recitation(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
                            create_recitation_request: CreateRecitationRequest):
    return await create_recitation_service(
        token=authentication_credential.credentials,
        create_recitation_request=create_recitation_request
    )

@recitation_router.get("",status_code=status.HTTP_200_OK,response_model=RecitationsResponse)
async def get_list_of_recitations(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],  skip: int = Query(default=0),
        limit: int = Query(default=10)):
    return await get_list_of_recitations_service(
        token=authentication_credential.credentials,
        skip=skip,
        limit=limit
    )