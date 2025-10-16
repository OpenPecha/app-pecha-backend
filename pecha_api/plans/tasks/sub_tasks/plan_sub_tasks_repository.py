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


def get_sub_tasks_by_task_id(db: Session, task_id: UUID) -> List[PlanSubTask]:
    return db.query(PlanSubTask).filter(PlanSubTask.task_id == task_id).order_by(PlanSubTask.display_order).all()

def delete_sub_tasks_bulk(db: Session, sub_tasks_ids: List[UUID]) -> None:
    if not sub_tasks_ids:
        return
    db.query(PlanSubTask).filter(PlanSubTask.id.in_(sub_tasks_ids)).delete()
    db.commit()

def update_sub_tasks_bulk(db: Session, sub_tasks: List[PlanSubTask]) -> None:
    if not sub_tasks:
        return
    for sub_task in sub_tasks:    
        db.query(PlanSubTask).filter(PlanSubTask.id == sub_task.id).update(
            display_order=sub_task.display_order,
            content=sub_task.content,
            content_type=sub_task.content_type
        )
    db.commit()