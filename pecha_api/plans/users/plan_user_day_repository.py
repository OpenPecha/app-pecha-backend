from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .plan_users_models import UserDayCompletion
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST

def save_user_day_completion(db: Session, user_day_completion: UserDayCompletion):
    try:
        db.add(user_day_completion)
        db.commit()
        db.refresh(user_day_completion)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=str(e.orig)).model_dump())

def delete_user_day_completion(db: Session, user_id: UUID, day_id: UUID) -> None:
    try:
        db.query(UserDayCompletion).filter(UserDayCompletion.user_id == user_id, UserDayCompletion.day_id == day_id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseError(error=BAD_REQUEST, message=str(e)).model_dump())

def get_user_day_completion_by_user_id_and_day_id(db: Session, user_id: UUID, day_id: UUID) -> UserDayCompletion:
    return db.query(UserDayCompletion).filter(UserDayCompletion.user_id == user_id, UserDayCompletion.day_id == day_id).first()