from pecha_api.recitations.recitations_models import Recitation
from pecha_api.recitations.recitations_response_models import CreateRecitationsRequest
from pecha_api.plans.authors.plan_authors_service import validate_and_extract_author_details
from pecha_api.db.database import SessionLocal
from pecha_api.recitations.recitations_repository import save_recitations

async def create_recitations_service(token: str, create_recitations_request: CreateRecitationsRequest) -> None:
    """create a new recitation"""
    validate_and_extract_author_details(token=token)
    with SessionLocal() as db:
        new_recitation = Recitation(
            title=create_recitations_request.title,
            audio_url=create_recitations_request.audio_url,
            text_id=create_recitations_request.text_id,
            content=create_recitations_request.content.model_dump(mode='json')
        )
        save_recitations(db=db, recitation=new_recitation)
        

    