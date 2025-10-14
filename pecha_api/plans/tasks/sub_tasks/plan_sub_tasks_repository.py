from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST, SUB_TASK_NOT_FOUND
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_models import PlanSubTask
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_response_model import UpdateSubTaskRequest
from pecha_api.error_contants import ErrorConstants


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

def get_sub_task_by_id(db: Session, sub_task_id: UUID) -> PlanSubTask:
    return db.query(PlanSubTask).filter(PlanSubTask.id == sub_task_id).first()

def update_sub_task(db: Session, sub_task_id: UUID, update_sub_task_request: UpdateSubTaskRequest) -> PlanSubTask:
    sub_task = get_sub_task_by_id(db=db, sub_task_id=sub_task_id)
    if not sub_task:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseError(error=BAD_REQUEST, message=ErrorConstants.SUB_TASK_NOT_FOUND).model_dump())
    sub_task.display_order = update_sub_task_request.target_display_order
    sub_task.content = update_sub_task_request.content
    db.commit()
    return sub_task