from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, asc, desc
from typing import Optional
from uuid import UUID
from pecha_api.plans.plans_models import Plan
from pecha_api.plans.items.plan_items_models import PlanItem
from pecha_api.plans.users.plan_users_model import UserPlanProgress
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.plans_response_models import PlansRepositoryResponse, PlanWithAggregates
from uuid import UUID

def save_plan(db: Session, plan: Plan):
    try:
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e.orig}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e.orig}")


def get_plans(
    db: Session,
    search: Optional[str],
    sort_by: str,
    sort_order: str,
    skip: int,
    limit: int,
) -> PlansRepositoryResponse:
    # Filters
    filters = [Plan.deleted_at.is_(None)]
    if search:
        filters.append(Plan.title.ilike(f"%{search}%"))

    # Aggregates (matching provided SQL): SUM of item day_number and COUNT DISTINCT of subscribers
    total_days_label = func.count(func.distinct(PlanItem.id)).label("total_days")
    subscription_count_label = func.count(func.distinct(UserPlanProgress.user_id)).label("subscription_count")

    # Base query with LEFT JOINs and GROUP BY
    query = (
        db.query(
            Plan,
            total_days_label,
            subscription_count_label,
        )
        .outerjoin(PlanItem, PlanItem.plan_id == Plan.id)
        .outerjoin(UserPlanProgress, UserPlanProgress.plan_id == Plan.id)
        .filter(*filters)
        .group_by(Plan.id)
    )

    # Sorting
    order = asc if sort_order == "asc" else desc
    sort_fields = {
        "created_at": Plan.created_at,
        "status": Plan.status,
        "total_days": total_days_label,
    }
    query = query.order_by(order(sort_fields.get(sort_by, Plan.created_at)))

    # Pagination
    rows = query.offset(skip).limit(limit).all()
    
    # Transform tuples into PlanWithAggregates objects using list comprehension
    plan_aggregates = [
        PlanWithAggregates(
            plan=plan,
            total_days=total_days,
            subscription_count=subscription_count
        )
        for plan, total_days, subscription_count in rows
    ]
    
    # Total count without pagination/joins
    total = db.query(func.count(Plan.id)).filter(*filters).scalar()
    return PlansRepositoryResponse(plan_info=plan_aggregates, total=total)

def get_plan_by_id(db: Session, plan_id: UUID) -> Plan:
    return db.query(Plan).filter(Plan.id == plan_id).first()

def get_plan_by_id_with_items_and_tasks(db: Session, plan_id: UUID) -> Plan:
    return db.query(Plan).filter(Plan.id == plan_id).options(joinedload(Plan.items), joinedload(Plan.tasks)).first()

def update_plan(db: Session, plan: Plan) -> Plan:

    try:
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error while updating plan: {e.orig}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update plan: {e.orig}"
        )
    except Exception as e:
        db.rollback()
        print(f"Error updating plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update plan: {str(e)}"
        )