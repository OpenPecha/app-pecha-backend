
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..plans.plans_models import Plan
from fastapi import HTTPException
from starlette import status

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
