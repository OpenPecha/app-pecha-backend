from typing import Optional
from starlette import status
from beanie import PydanticObjectId
from pecha_api.cataloger.cataloger_response_model import CatalogedTextsDetailsResponse
from pecha_api.error_contants import ErrorConstants
from ..config import get
from fastapi import HTTPException



async def get_cataloged_texts_details(text_id: str, skip: int, limit: int) -> Optional[CatalogedTextsDetailsResponse]:
    if text_id is None:
        return None
    #we will call external api and add status field here
    return None
