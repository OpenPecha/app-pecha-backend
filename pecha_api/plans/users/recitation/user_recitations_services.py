from pecha_api.db.database import SessionLocal
from pecha_api.plans.users.recitation.user_recitations_models import UserRecitations
from pecha_api.plans.users.recitation.user_recitations_repository import save_user_recitation
from pecha_api.plans.users.recitation.user_recitations_response_models import CreateUserRecitationRequest
from pecha_api.users.users_service import validate_and_extract_user_details
from pecha_api.texts.texts_utils import TextUtils

async def create_user_recitation_service(token: str, create_user_recitation_request: CreateUserRecitationRequest) -> None:
    """create a new user recitation"""
    current_user=validate_and_extract_user_details(token=token)
    with SessionLocal() as db:
        await TextUtils.validate_text_exists(text_id=str(create_user_recitation_request.text_id))
        new_user_recitations = UserRecitations(
            user_id=current_user.id,
            text_id=create_user_recitation_request.text_id
        )
        save_user_recitation(db=db, user_recitations=new_user_recitations)