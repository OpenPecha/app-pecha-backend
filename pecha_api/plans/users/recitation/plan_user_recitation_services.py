from pecha_api.db.database import SessionLocal
from pecha_api.plans.recitation.plan_recitation_repository import check_recitation_exists
from pecha_api.plans.users.recitation.plan_user_recitation_model import UserRecitation
from pecha_api.plans.users.recitation.plan_user_recitation_repository import save_user_recitation
from pecha_api.plans.users.recitation.plan_user_recitation_response_models import CreateUserRecitationRequest
from pecha_api.users.users_service import validate_and_extract_user_details

def create_user_recitation_service(token: str, create_user_recitation_request: CreateUserRecitationRequest) -> None:
    """create a new user recitation"""
    current_user=validate_and_extract_user_details(token=token)
    with SessionLocal() as db:
        recitation = check_recitation_exists(db=db, recitation_id=create_user_recitation_request.recitation_id)
        new_user_recitation = UserRecitation(
            user_id=current_user.id,
            recitation_id=recitation.id
        )
        save_user_recitation(db=db, user_recitation=new_user_recitation)