from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .user_plan_progress_models import UserPlanProgress
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST
from typing import List

def save_plan_progress(db: Session, plan_progress: UserPlanProgress):
    try:
        db.add(plan_progress)
        db.commit()
        db.refresh(plan_progress)
        return plan_progress
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e.orig}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=e.orig).model_dump())

def get_plan_progress(db: Session, plan_id: UUID) -> List[UserPlanProgress]:
    return db.query(UserPlanProgress).filter(UserPlanProgress.plan_id == plan_id).all()