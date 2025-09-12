
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from starlette import status

from pecha_api.db.database import SessionLocal
from pecha_api.plans.items.plan_items_repository import get_plan_item
from pecha_api.plans.tasks.plan_tasks_models import PlanTask
from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO

def create_task(create_task_request: CreateTaskRequest, plan_id: str, day_id: str, created_by: str) -> TaskDTO:
    
    with SessionLocal() as db:

        plan_item = get_plan_item(db=db, plan_id=plan_id, day_id=day_id)
        max_order = db.query(func.max(PlanTask.display_order)).filter(PlanTask.plan_item_id == plan_item.id).scalar() or 0
        display_order:int = max_order + 1
        
        new_task = PlanTask(
            plan_item_id=plan_item.id,
            title=create_task_request.title,
            content_type=create_task_request.content_type,
            content=create_task_request.content,
            display_order=display_order,
            estimated_time=create_task_request.estimated_time,
            created_by=created_by,
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
            title=new_task.title,
            description=create_task_request.description,
            content_type=new_task.content_type,
            content=new_task.content,
            display_order=new_task.display_order,
            estimated_time=int(new_task.estimated_time),
        )
