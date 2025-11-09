from typing import List
from sqlalchemy.orm import Session
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.recitation.plan_recitation_models import Recitation
from sqlalchemy.exc import IntegrityError
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

def get_list_of_recitations(db: Session) -> List[Recitation]:
    return db.query(Recitation).all()