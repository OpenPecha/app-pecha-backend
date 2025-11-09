from pecha_api.plans.recitation.plan_recitation_models import Recitation
from pecha_api.plans.recitation.plan_recitation_response_models import CreateRecitationRequest
from pecha_api.plans.authors.plan_authors_service import validate_and_extract_author_details
from pecha_api.db.database import SessionLocal
from pecha_api.plans.recitation.plan_recitation_repository import save_recitation
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
        

    