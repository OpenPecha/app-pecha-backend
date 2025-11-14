from uuid import UUID
from pecha_api.db.database import SessionLocal
from pecha_api.plans.users.recitation.user_recitations_models import UserRecitations
from pecha_api.plans.users.recitation.user_recitations_repository import save_user_recitation, get_user_recitations_by_user_id, delete_user_recitation
from pecha_api.plans.users.recitation.user_recitations_response_models import (
    CreateUserRecitationRequest, 
    UserRecitationsResponse, 
    UserRecitationDTO
)
from pecha_api.users.users_service import validate_and_extract_user_details
from pecha_api.texts.texts_utils import TextUtils
from pecha_api.texts.texts_repository import get_texts_by_ids

async def create_user_recitation_service(token: str, create_user_recitation_request: CreateUserRecitationRequest) -> None:
    current_user=validate_and_extract_user_details(token=token)
    with SessionLocal() as db:
        await TextUtils.validate_text_exists(text_id=str(create_user_recitation_request.text_id))
        new_user_recitations = UserRecitations(
            user_id=current_user.id,
            text_id=create_user_recitation_request.text_id
        )
        save_user_recitation(db=db, user_recitations=new_user_recitations)


async def get_user_recitations_service(token: str) -> UserRecitationsResponse:
    current_user = validate_and_extract_user_details(token=token)
    
    with SessionLocal() as db:
        user_recitations = get_user_recitations_by_user_id(db=db, user_id=current_user.id)
        
        if not user_recitations:
            return UserRecitationsResponse(recitations=[])
        
        text_ids = [str(recitation.text_id) for recitation in user_recitations]
        texts_dict = await get_texts_by_ids(text_ids=text_ids)
        
        recitations_dto = [
            UserRecitationDTO(title=texts_dict[str(recitation.text_id)].title, text_id=recitation.text_id)
            for recitation in user_recitations
            if str(recitation.text_id) in texts_dict
        ]
        
        return UserRecitationsResponse(recitations=recitations_dto)


async def delete_user_recitation_service(token: str, recitation_id: UUID) -> None:
    current_user = validate_and_extract_user_details(token=token)

    with SessionLocal() as db:
        delete_user_recitation(db=db, user_id=current_user.id, recitation_id=recitation_id)