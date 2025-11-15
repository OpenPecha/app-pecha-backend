from typing import Optional
from fastapi import APIRouter, Query
from starlette import status

from pecha_api.recitations.recitations_response_models import RecitationsResponse
from pecha_api.recitations.recitations_services import get_list_of_recitations_service

recitation_router=APIRouter(
    prefix="/recitations",
    tags=["Recitations"],
)

@recitation_router.get("",status_code=status.HTTP_200_OK,response_model=RecitationsResponse)
async def get_list_of_recitations(search: Optional[str] = Query(None, description="Search by Recitation title"),language: str = Query()):
    return await get_list_of_recitations_service(search=search, language=language)