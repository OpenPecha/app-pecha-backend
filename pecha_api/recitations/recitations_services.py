from typing import Optional
from pecha_api.collections.collections_repository import get_all_collections_by_parent, get_collection_id_by_slug
from pecha_api.collections.collections_service import get_collection
from pecha_api.recitations.recitations_repository import apply_search_recitation_title_filter
from pecha_api.recitations.recitations_response_models import RecitationDTO, RecitationsResponse
from pecha_api.texts.texts_repository import get_all_texts_by_collection
from pecha_api.texts.texts_service import get_root_text_by_collection_id
from fastapi import HTTPException
from starlette import status
from pecha_api.error_contants import ErrorConstants


async def get_list_of_recitations_service(search: Optional[str] = None, language: str = "en") -> RecitationsResponse:
    collection_id = await get_collection_id_by_slug(slug="Liturgy")
    if collection_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.COLLECTION_NOT_FOUND)
    
    text_id, text_title = await get_root_text_by_collection_id(collection_id=collection_id, language=language)

    # if search:
    #     list_of_texts=apply_search_recitation_title_filter(text=list_of_texts, search=search)
    recitations_dto = [RecitationDTO(title=text_title, text_id=text_id)]
    return RecitationsResponse(recitations=recitations_dto)
