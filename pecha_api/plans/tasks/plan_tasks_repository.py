
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from starlette import status

from pecha_api.db.database import SessionLocal
from pecha_api.plans.items.plan_items_models import PlanItem
from pecha_api.plans.tasks.plan_tasks_models import PlanTask
from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO


def _get_plan_item(db: Session, plan_id: UUID, day_id: UUID) -> PlanItem:
    plan_item = (
        db.query(PlanItem)
        .filter(PlanItem.id == day_id, PlanItem.plan_id == plan_id)
        .first()
    )
    if not plan_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan day not found")
    return plan_item


def _next_display_order(db: Session, plan_item_id: UUID) -> int:
    max_order = (
        db.query(func.max(PlanTask.display_order))
        .filter(PlanTask.plan_item_id == plan_item_id)
        .scalar()
    )
    return (max_order or 0) + 1


def create_task(create_task_request: CreateTaskRequest, plan_id: UUID, day_id: UUID, created_by: str) -> TaskDTO:
    with SessionLocal() as db:
        plan_item = _get_plan_item(db=db, plan_id=plan_id, day_id=day_id)
        display_order = _next_display_order(db=db, plan_item_id=plan_item.id)

        new_task = PlanTask(
            plan_item_id=plan_item.id,
            title=create_task_request.title,
            content_type=create_task_request.content_type,
            content=create_task_request.content,
            display_order=display_order,
            estimated_time=create_task_request.estimated_time,
            is_required=True,
            created_by=created_by,
            updated_by=created_by,
        )

        try:
            db.add(new_task)
            db.commit()
            db.refresh(new_task)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))

        return TaskDTO(
            id=new_task.id,
            title=new_task.title or "",
            description=create_task_request.description,
            content_type=new_task.content_type,
            content=new_task.content,
            estimated_time=new_task.estimated_time,
        )


