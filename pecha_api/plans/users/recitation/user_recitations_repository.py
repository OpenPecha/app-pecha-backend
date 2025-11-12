from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from starlette import status
from typing import List
from uuid import UUID
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST
from pecha_api.plans.users.recitation.user_recitations_models import UserRecitations

def save_user_recitation(db: Session, user_recitations: UserRecitations) -> None:
    try:
        db.add(user_recitations)
        db.commit()
        db.refresh(user_recitations)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=str(e.orig)).model_dump())

def get_user_recitations_by_user_id(db: Session, user_id: UUID) -> List[UserRecitations]:
    return db.query(UserRecitations).filter(UserRecitations.user_id == user_id).all()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=str(e.orig)).model_dump())
