from pecha_api.texts.texts_models import Text
from pecha_api.texts.texts_enums import TextType
from typing import List
from fastapi import HTTPException
from starlette import status

from pecha_api.error_contants import ErrorConstants

# Texts
from pecha_api.texts.texts_utils import TextUtils
from pecha_api.texts.texts_response_models import TextDTO
from pecha_api.texts.texts_repository import get_texts_by_group_id

# Recitations
from pecha_api.recitations.recitations_response_models import (
    RecitationDTO, 
    RecitationsResponse, 
    RecitationDetailsRequest, 
    RecitationDetailsResponse)

async def get_list_of_recitations_service() -> RecitationsResponse:
    recitations = await Text.get_list_of_recitations(type=TextType.RECITATION)
    recitations_dto = [RecitationDTO(title=recitation.title, text_id=recitation.id) for recitation in recitations]
    return RecitationsResponse(recitations=recitations_dto)

async def get_recitation_details_service(text_id: str, recitation_details_request: RecitationDetailsRequest) -> RecitationDetailsResponse:
    is_valid_text: bool = await TextUtils.validate_text_exists(text_id=text_id)
    if not is_valid_text:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)

    text_detail: TextDTO = await TextUtils.get_text_detail_by_id(text_id=text_id)
    group_id: str = text_detail.group_id
    texts: List[TextDTO] = await get_texts_by_group_id(group_id=group_id, skip=0, limit=10)
    
    return RecitationDetailsResponse(recitation=recitation)