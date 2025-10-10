
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .plan_items_models import PlanItem
from fastapi import HTTPException
from starlette import status
from sqlalchemy import func, asc
from uuid import UUID
from typing import List
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST, PLAN_DAY_NOT_FOUND
from uuid import UUID

def save_plan_items(db: Session, plan_items: List[PlanItem]):
    try:
        db.add_all(plan_items)
        db.commit()
        for item in plan_items:
            db.refresh(item)
        return plan_items
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e.orig}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseError(error=BAD_REQUEST, 
            message=e.orig).model_dump()
        )


def get_plan_item_by_id(db: Session, day_id: UUID) -> PlanItem:
    return db.query(PlanItem).filter(PlanItem.id == day_id).first()

def get_plan_item(db: Session, plan_id: UUID, day_id: UUID) -> PlanItem:
    plan_item = (
        db.query(PlanItem)
        .filter(PlanItem.id == day_id, PlanItem.plan_id == plan_id)
        .first()
    )
    if not plan_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ResponseError(
                error=PLAN_DAY_NOT_FOUND, 
                message=PLAN_DAY_NOT_FOUND).model_dump()
            )
    return plan_item
def save_plan_item(db: Session, plan_item: PlanItem) -> PlanItem:
    try:
        db.add(plan_item)
        db.commit()
        db.refresh(plan_item)
        return plan_item
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e.orig}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=e.orig).model_dump())

def get_plan_items_by_plan_id(db: Session, plan_id: UUID) -> List[PlanItem]:
    return (
        db.query(PlanItem)
        .filter(PlanItem.plan_id == plan_id)
        .order_by(asc(PlanItem.day_number))
        .all()
    )

def get_last_day_number(db: Session, plan_id: UUID) -> int:
    return db.query(func.max(PlanItem.day_number)).filter(PlanItem.plan_id == plan_id).scalar() or 0
