from pecha_api.collections.collections_repository import get_all_collections_by_parent, get_collection_id_by_slug
from pecha_api.recitations.recitations_response_models import RecitationDTO, RecitationsResponse
from pecha_api.texts.texts_service import get_root_text_by_collection_id

async def get_list_of_recitations_service(language: str) -> RecitationsResponse:
    collection_id = await get_collection_id_by_slug(slug="Liturgy")
    collections = await get_all_collections_by_parent(parent_id=collection_id)
    list_of_collections = [str(collection.id) for collection in collections]
    list_of_texts = []
    for collection_id in list_of_collections:
        text_id, text_title = await get_root_text_by_collection_id(collection_id=collection_id, language=language)
        if text_id is not None and text_title is not None:
            list_of_texts.append((text_id, text_title))

    recitations_dto = [RecitationDTO(title=text_title, text_id=text_id) for text_id, text_title in list_of_texts]
    return RecitationsResponse(recitations=recitations_dto)
