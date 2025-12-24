from __future__ import annotations

from fastapi import APIRouter
from fastapi.security import HTTPBearer
from starlette import status
from pecha_api.cataloger.cataloger_service import get_cataloged_texts_details
from pecha_api.cataloger.cataloger_response_model import CatalogedTextsDetailsResponse


oauth2_scheme = HTTPBearer()
cataloger_router = APIRouter(
    prefix="/cataloger",
    tags=["cataloger"]
)


@cataloger_router.get("/texts/{text_id}", status_code=status.HTTP_200_OK, response_model=CatalogedTextsDetailsResponse)
async def read_cataloged_texts_details(
        text_id: str
)->CatalogedTextsDetailsResponse:
    return await get_cataloged_texts_details(
        text_id=text_id
    )