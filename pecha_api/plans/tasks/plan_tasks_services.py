from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO
from pecha_api.plans.tasks.plan_tasks_repository import save_task, get_task_by_id, delete_task
from pecha_api.plans.authors.plan_authors_service import validate_and_extract_author_details
from uuid import UUID
from pecha_api.db.database import SessionLocal
from pecha_api.plans.items.plan_items_repository import get_plan_item
from pecha_api.plans.tasks.plan_tasks_models import PlanTask
from sqlalchemy import func
from pecha_api.plans.response_message import FORBIDDEN, UNAUTHORIZED_TASK_DELETE
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.auth.plan_auth_models import ResponseError


async def create_new_task(token: str, create_task_request: CreateTaskRequest, plan_id: UUID, day_id: UUID) -> TaskDTO:
    current_author = validate_and_extract_author_details(token=token)

    with SessionLocal() as db:

        plan_item = get_plan_item(db=db, plan_id=plan_id, day_id=day_id)
        
        max_order = db.query(func.max(PlanTask.display_order)).filter(PlanTask.plan_item_id == plan_item.id).scalar() or 0
        display_order:int = max_order + 1

        new_task = PlanTask(
            plan_item_id=plan_item.id,
            title=create_task_request.title,
            display_order=display_order,
            estimated_time=create_task_request.estimated_time,
            created_by=current_author.email,
        )

    saved_task = save_task(db=db,new_task=new_task)

    return TaskDTO(
        id=saved_task.id,
        title=saved_task.title,
        display_order=saved_task.display_order,
        estimated_time=saved_task.estimated_time,
    )

async def delete_task_by_id(task_id: UUID, token: str):
    current_author = validate_and_extract_author_details(token=token)
    
    with SessionLocal() as db:
        task = get_task_by_id(db=db, task_id=task_id)
        if task.created_by != current_author.email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ResponseError(error=FORBIDDEN, message=UNAUTHORIZED_TASK_DELETE).model_dump())
        delete_task(db=db, task_id=task_id)