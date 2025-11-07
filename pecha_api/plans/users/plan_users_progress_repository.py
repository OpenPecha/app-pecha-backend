from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pecha_api.plans.users.plan_users_response_models import EnrolledUserPlan
from .plan_users_models import UserPlanProgress
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST
from typing import List

def save_plan_progress(db: Session, plan_progress: EnrolledUserPlan):
    try:
        db.add(plan_progress)
        db.commit()
        db.refresh(plan_progress)
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e.orig}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=e.orig).model_dump())

def get_plan_progress(db: Session, plan_id: UUID) -> List[UserPlanProgress]:
    return db.query(UserPlanProgress).filter(UserPlanProgress.plan_id == plan_id).all()

def get_plan_progress_by_user_id_and_plan_id(db: Session, user_id: UUID, plan_id: UUID) -> UserPlanProgress:
    return db.query(UserPlanProgress).filter(UserPlanProgress.user_id == user_id, UserPlanProgress.plan_id == plan_id).first()