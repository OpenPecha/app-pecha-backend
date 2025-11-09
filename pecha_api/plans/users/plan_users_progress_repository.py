from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from pecha_api.plans.users.plan_users_response_models import EnrolledUserPlan
from .plan_users_models import UserPlanProgress
from pecha_api.plans.plans_models import Plan
from pecha_api.plans.items.plan_items_models import PlanItem
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST
from typing import List, Optional, Tuple

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


def get_user_enrolled_plans_with_details(db: Session,user_id: UUID, status: Optional[str] = None,skip: int = 0, limit: int = 20,order_by_field = None,order_desc: bool = True
) -> Tuple[List[Tuple[UserPlanProgress, Plan, int]], int]:

    if order_by_field is None:
        order_by_field = UserPlanProgress.started_at
    
    days_subquery = db.query(
        PlanItem.plan_id,
        func.count(PlanItem.id).label('total_days')
    ).group_by(PlanItem.plan_id).subquery()
    
    query = db.query(
        UserPlanProgress, 
        Plan, 
        func.coalesce(days_subquery.c.total_days, 0).label('total_days')
    ).join(
        Plan, UserPlanProgress.plan_id == Plan.id
    ).outerjoin(
        days_subquery, Plan.id == days_subquery.c.plan_id
    ).filter(
        UserPlanProgress.user_id == user_id
    )
    
    if status:
        query = query.filter(UserPlanProgress.status == status)
    
    total = query.count()
    
    if order_desc:
        query = query.order_by(order_by_field.desc())
    else:
        query = query.order_by(order_by_field)
    
    results = query.offset(skip).limit(limit).all()
    
    return results, total