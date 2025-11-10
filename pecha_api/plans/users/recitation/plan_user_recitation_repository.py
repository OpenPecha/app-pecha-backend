from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST
from pecha_api.plans.users.recitation.plan_user_recitation_model import UserRecitation
from pecha_api.error_contants import ErrorConstants


def save_user_recitation(db: Session, user_recitation: UserRecitation) -> None:
    try:
        db.add(user_recitation)
        db.commit()
        db.refresh(user_recitation)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=str(e.orig)).model_dump())

def get_user_recitation_by_id(db: Session, user_id: UUID, recitation_id: UUID) -> UserRecitation:
    return db.query(UserRecitation).filter(UserRecitation.user_id == user_id, UserRecitation.recitation_id == recitation_id).first()

def delete_user_recitation_repository(db: Session, user_recitation: UserRecitation) -> None:
    try:
        db.delete(user_recitation)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=str(e)).model_dump())