from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.recitation.plan_recitation_models import Recitation
from sqlalchemy.exc import IntegrityError
from pecha_api.error_contants import ErrorConstants
from fastapi import HTTPException
from starlette import status

from pecha_api.plans.response_message import BAD_REQUEST

def save_recitation(db: Session, recitation: Recitation) -> None:
    try:
        db.add(recitation)
        db.commit()
        db.refresh(recitation)
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e.orig}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=str(e.orig)).model_dump())

def list_of_recitations(db: Session, skip: int, limit: int) -> List[Recitation]:
    return db.query(Recitation).offset(skip).limit(limit).all()

def count_of_recitations(db: Session) -> int:
    return db.query(Recitation).count()

def check_recitation_exists(db: Session, recitation_id: UUID) -> Recitation:
    recitation = db.query(Recitation).filter(Recitation.id == recitation_id).first()
    if recitation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=ErrorConstants.RECITATION_NOT_FOUND).model_dump())
    return recitation