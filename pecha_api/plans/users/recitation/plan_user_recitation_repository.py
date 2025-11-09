from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST
from pecha_api.plans.users.recitation.plan_user_recitation_model import UserRecitation

def save_user_recitation(db: Session, user_recitation: UserRecitation) -> None:
    try:
        db.add(user_recitation)
        db.commit()
        print(f"User recitation saved: {user_recitation}")
        db.refresh(user_recitation)
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e.orig}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=str(e.orig)).model_dump())