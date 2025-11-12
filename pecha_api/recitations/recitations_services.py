from pecha_api.texts.texts_models import Text
from pecha_api.texts.texts_enums import TextType
from pecha_api.recitations.recitations_response_models import RecitationDTO, RecitationsResponse

async def get_list_of_recitations_service() -> RecitationsResponse:
    recitations = await Text.get_list_of_recitations(type=TextType.RECITATION)
    recitations_dto = [RecitationDTO(title=recitation.title, text_id=recitation.id) for recitation in recitations]
    return RecitationsResponse(recitations=recitations_dto)
