from fastapi import APIRouter
from starlette import status
from fastapi.security import HTTPBearer

from pecha_api.recitations.recitations_response_models import RecitationsResponse
from pecha_api.recitations.recitations_services import get_list_of_recitations_service

oauth2_scheme=HTTPBearer()
recitation_router=APIRouter(
    prefix="/cms/recitations",
    tags=["Recitations"],
)

@recitation_router.get("",status_code=status.HTTP_200_OK,response_model=RecitationsResponse)
async def get_list_of_recitations():
    return await get_list_of_recitations_service()