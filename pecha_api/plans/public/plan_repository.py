from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from typing import Optional
from uuid import UUID
from pecha_api.plans.plans_models import Plan
from pecha_api.plans.items.plan_items_models import PlanItem
from pecha_api.plans.users.plan_users_model import UserPlanProgress
from pecha_api.plans.plans_enums import PlanStatus
from pecha_api.plans.plans_response_models import PlanWithAggregates


def get_published_plans_from_db(db: Session, skip: int = 0, limit: int = 20):

    total_days_label = func.count(func.distinct(PlanItem.id)).label("total_days")
    subscription_count_label = func.count(func.distinct(UserPlanProgress.user_id)).label("subscription_count")
    
    query = (
        db.query(
            Plan,
            total_days_label,
            subscription_count_label,
        )
        .outerjoin(PlanItem, PlanItem.plan_id == Plan.id)
        .outerjoin(UserPlanProgress, UserPlanProgress.plan_id == Plan.id)
        .options(selectinload(Plan.author))
        .filter(
            Plan.deleted_at.is_(None),
            Plan.status == PlanStatus.PUBLISHED
        )
        .group_by(Plan.id)
    )
    
    rows = query.offset(skip).limit(limit).all()
    
    plan_aggregates = [
        PlanWithAggregates(
            plan=plan,
            total_days=total_days,
            subscription_count=subscription_count
        )
        for plan, total_days, subscription_count in rows
    ]
    
    return plan_aggregates


def get_published_plans_count(db: Session) -> int:

    return db.query(func.count(Plan.id)).filter(
        Plan.deleted_at.is_(None),
        Plan.status == PlanStatus.PUBLISHED
    ).scalar()


def get_published_plan_by_id(db: Session, plan_id: UUID) -> Optional[Plan]:
    return db.query(Plan).options(selectinload(Plan.author)).filter(
            Plan.id == plan_id,
            Plan.status == PlanStatus.PUBLISHED,
            Plan.deleted_at.is_(None)
        ).first()


def get_plan_items_by_plan_id(db: Session, plan_id: UUID) -> list[PlanItem]:
    return db.query(PlanItem).filter(PlanItem.plan_id == plan_id).order_by(PlanItem.day_number).all()


def get_plan_item_by_day_number(db: Session, plan_id: UUID, day_number: int) -> Optional[PlanItem]:
    return db.query(PlanItem).filter(
            PlanItem.plan_id == plan_id,
            PlanItem.day_number == day_number
        ).first()