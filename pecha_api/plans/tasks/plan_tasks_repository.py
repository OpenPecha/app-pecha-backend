
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from starlette import status
from typing import List
from sqlalchemy import asc

from pecha_api.db.database import SessionLocal
from pecha_api.plans.items.plan_items_repository import get_plan_item
from pecha_api.plans.tasks.plan_tasks_models import PlanTask
from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST


def save_task(db: Session, new_task: PlanTask):
    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseError(error=BAD_REQUEST, message=str(e.orig)).model_dump())

def get_tasks_by_item_ids(db: Session, plan_item_ids: List[UUID]) -> List[PlanTask]:
    if not plan_item_ids:
        return {}

    tasks = (
        db.query(PlanTask)
        .filter(PlanTask.plan_item_id.in_(plan_item_ids))
        .order_by(asc(PlanTask.plan_item_id), asc(PlanTask.display_order))
        .all()
    )

    return tasks