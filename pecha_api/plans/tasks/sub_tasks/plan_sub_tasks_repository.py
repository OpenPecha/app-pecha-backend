from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_models import PlanSubTask


def get_max_display_order_for_sub_task(db: Session, task_id: UUID) -> int:
    max_order = (
        db.query(func.max(PlanSubTask.display_order))
        .filter(PlanSubTask.task_id == task_id)
        .scalar()
        or 0
    )
    return int(max_order)


def save_sub_tasks_bulk(db: Session, sub_tasks: List[PlanSubTask]) -> List[PlanSubTask]:
    if not sub_tasks:
        return []
    try:
        db.add_all(sub_tasks)
        db.commit()
        return sub_tasks
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseError(error=BAD_REQUEST, message=str(e.orig)).model_dump(),
        )

