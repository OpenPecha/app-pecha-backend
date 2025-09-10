
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .plan_items_models import PlanItem
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.error_contants import BAD_REQUEST

def save_plan_item(db: Session, plan_item: PlanItem):
    try:
        db.add(plan_item)
        db.commit()
        db.refresh(plan_item)
        return plan_item
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e.orig}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=e.orig).model_dump())
