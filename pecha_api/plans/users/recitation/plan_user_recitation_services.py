from uuid import UUID

from fastapi import HTTPException
from starlette import status
from pecha_api.db.database import SessionLocal
from pecha_api.error_contants import ErrorConstants
from pecha_api.plans.recitation.plan_recitation_repository import check_recitation_exists
from pecha_api.plans.response_message import BAD_REQUEST
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.users.recitation.plan_user_recitation_model import UserRecitation
from pecha_api.plans.users.recitation.plan_user_recitation_repository import delete_user_recitation_repository, get_user_recitation_by_id, save_user_recitation
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

def delete_user_recitation_service(token: str, recitation_id: UUID) -> None:
    """delete a user recitation"""
    current_user=validate_and_extract_user_details(token=token)
    with SessionLocal() as db:
        user_recitation = get_user_recitation_by_id(db=db, user_id=current_user.id, recitation_id=recitation_id)
        if user_recitation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=ErrorConstants.RECITATION_NOT_FOUND).model_dump())
        delete_user_recitation_repository(db=db, user_recitation=user_recitation)