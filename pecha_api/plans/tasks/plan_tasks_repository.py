from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException
from starlette import status
from typing import List, Optional
from sqlalchemy import asc

from pecha_api.db.database import SessionLocal
from pecha_api.plans.items.plan_items_repository import get_plan_item
from pecha_api.plans.tasks.plan_tasks_models import PlanTask
from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.response_message import BAD_REQUEST, TASK_NOT_FOUND 


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

def get_task_by_id(db: Session, task_id: UUID) -> PlanTask:
    task = (
        db.query(PlanTask)
        .options(joinedload(PlanTask.sub_tasks))
        .filter(PlanTask.id == task_id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ResponseError(error=BAD_REQUEST, message=TASK_NOT_FOUND).model_dump())
    return task

def delete_task(db: Session, task_id: UUID):
    task = get_task_by_id(db=db, task_id=task_id)
    try:
        db.delete(task)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseError(error=BAD_REQUEST, message=str(e)).model_dump())
    return db.query(PlanTask).filter(PlanTask.id == task_id).first()

def update_task_day(db: Session, task_id: UUID, target_day_id: UUID, display_order: int) -> PlanTask:
    task = get_task_by_id(db=db, task_id=task_id)
    task.plan_item_id = target_day_id
    task.display_order = display_order
    db.commit()
    return task

def update_task_title(db: Session, task_id: UUID, title: str) -> PlanTask:
    task = get_task_by_id(db=db, task_id=task_id)
    task.title = title
    db.commit()
    db.refresh(task)
    return task

def get_tasks_by_plan_item_id(db: Session, plan_item_id: UUID) -> List[PlanTask]:
    return db.query(PlanTask).filter(PlanTask.plan_item_id == plan_item_id).order_by(PlanTask.display_order).all()

def update_task_order_by_id(db: Session, task_id: UUID, display_order: int) -> PlanTask:
    task = get_task_by_id(db=db, task_id=task_id)
    task.display_order = display_order
    db.commit()
    return task