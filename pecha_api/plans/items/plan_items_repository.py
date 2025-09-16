
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .plan_items_models import PlanItem
from fastapi import HTTPException
from starlette import status
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