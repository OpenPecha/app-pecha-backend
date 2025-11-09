from typing import List
from pecha_api.plans.recitation.plan_recitation_models import Recitation
from pecha_api.plans.recitation.plan_recitation_response_models import CreateRecitationRequest, RecitationDTO
from pecha_api.plans.authors.plan_authors_service import validate_and_extract_author_details
from pecha_api.users.users_service import validate_and_extract_user_details
from pecha_api.db.database import SessionLocal
from pecha_api.plans.recitation.plan_recitation_repository import list_of_recitations, save_recitation
from pecha_api.texts.texts_utils import TextUtils

async def create_recitation_service(token: str, create_recitation_request: CreateRecitationRequest) -> None:
    """create a new recitation"""
    validate_and_extract_author_details(token=token)
    await TextUtils.validate_text_exists(str(create_recitation_request.text_id))
    with SessionLocal() as db:
        new_recitation = Recitation(
            title=create_recitation_request.title,
            audio_url=create_recitation_request.audio_url,
            text_id=create_recitation_request.text_id,
            content=create_recitation_request.content
        )
        save_recitation(db=db, recitation=new_recitation)
        
async def get_list_of_recitations_service(token: str) -> List[RecitationDTO]:
    """get list of recitations"""
    validate_and_extract_user_details(token=token)
    with SessionLocal() as db:
        recitations = list_of_recitations(db=db)
        return [RecitationDTO(id=recitation.id, title=recitation.title, audio_url=recitation.audio_url, text_id=recitation.text_id, content=recitation.content) for recitation in recitations]