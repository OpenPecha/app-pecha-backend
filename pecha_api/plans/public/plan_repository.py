from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, asc, desc, or_
from typing import Optional
from uuid import UUID
from pecha_api.plans.plans_models import Plan
from pecha_api.plans.items.plan_items_models import PlanItem
from pecha_api.plans.users.plan_users_model import UserPlanProgress
from pecha_api.plans.plans_enums import PlanStatus
from pecha_api.plans.plans_response_models import PlansRepositoryResponse, PlanWithAggregates
from fastapi import HTTPException
from starlette import status


def get_published_plans_from_db(db: Session, search: Optional[str] = None, language: Optional[str] = None, sort_by: str = "title", sort_order: str = "asc", skip: int = 0, limit: int = 20) -> PlansRepositoryResponse:

    try:
        filters = [
            Plan.deleted_at.is_(None),
            Plan.status == PlanStatus.PUBLISHED
        ]
        
        if search:
            filters.append(Plan.title.ilike(f"%{search}%"))
        
        if language:
            filters.append(func.lower(Plan.language) == language.lower())
        
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
            .filter(*filters)
            .group_by(Plan.id)
        )
        
        order = asc if sort_order == "asc" else desc
        sort_fields = {
            "title": Plan.title,
            "total_days": total_days_label,
            "subscription_count": subscription_count_label,
        }
        sort_field = sort_fields.get(sort_by, Plan.title)
        query = query.order_by(order(sort_field))
        
        rows = query.offset(skip).limit(limit).all()
        
        plan_aggregates = [
            PlanWithAggregates(
                plan=plan,
                total_days=total_days,
                subscription_count=subscription_count
            )
            for plan, total_days, subscription_count in rows
        ]
        
        total = db.query(func.count(Plan.id)).filter(*filters).scalar()
        
        return PlansRepositoryResponse(plan_info=plan_aggregates, total=total)
    
    except Exception as e:
        db.rollback()
        print(f"Error fetching published plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch published plans: {str(e)}"
        )


def get_published_plan_by_id(db: Session, plan_id: UUID) -> Optional[Plan]:
 
    try:
        return (
            db.query(Plan)
            .options(selectinload(Plan.author))
            .filter(
                Plan.id == plan_id,
                Plan.status == PlanStatus.PUBLISHED,
                Plan.deleted_at.is_(None)
            )
            .first()
        )
    except Exception as e:
        db.rollback()
        print(f"Error fetching published plan by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch plan: {str(e)}"
        )


def get_plan_items_by_plan_id(db: Session, plan_id: UUID) -> list[PlanItem]:
    try:
        plan = get_published_plan_by_id(db, plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found or not published"
            )
        
        return (
            db.query(PlanItem)
            .filter(PlanItem.plan_id == plan_id)
            .order_by(PlanItem.day_number)
            .all()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error fetching plan items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch plan days: {str(e)}"
        )


def get_plan_item_by_day_number(db: Session, plan_id: UUID, day_number: int) -> Optional[PlanItem]:
    try:
        plan = get_published_plan_by_id(db, plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found or not published"
            )
        
        return (
            db.query(PlanItem)
            .filter(
                PlanItem.plan_id == plan_id,
                PlanItem.day_number == day_number
            )
            .first()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error fetching plan item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch plan day: {str(e)}"
        )