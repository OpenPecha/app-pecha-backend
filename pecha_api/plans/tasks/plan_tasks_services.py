from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO, UpdateTaskDayRequest, UpdatedTaskDayResponse
from pecha_api.plans.tasks.plan_tasks_repository import save_task, update_task_day
from pecha_api.plans.authors.plan_authors_service import validate_and_extract_author_details
from uuid import UUID
from fastapi import HTTPException
from pecha_api.db.database import SessionLocal
from pecha_api.plans.items.plan_items_repository import get_plan_item, get_plan_item_by_id
from pecha_api.plans.tasks.plan_tasks_models import PlanTask
from sqlalchemy import func
from pecha_api.plans.response_message import PLAN_DAY_NOT_FOUND, BAD_REQUEST, TASK_SAME_DAY_NOT_ALLOWED
from pecha_api.plans.auth.plan_auth_models import ResponseError

def _get_max_display_order(plan_item_id: UUID) -> int:
    with SessionLocal() as db:
        max_order = db.query(func.max(PlanTask.display_order)).filter(PlanTask.plan_item_id == plan_item_id).scalar() or 0
        return max_order

async def create_new_task(token: str, create_task_request: CreateTaskRequest, plan_id: UUID, day_id: UUID) -> TaskDTO:
    current_author = validate_and_extract_author_details(token=token)

    with SessionLocal() as db:

        plan_item = get_plan_item(db=db, plan_id=plan_id, day_id=day_id)
        
        display_order:int = _get_max_display_order(plan_item_id=plan_item.id) + 1

        new_task = PlanTask(
            plan_item_id=plan_item.id,
            title=create_task_request.title,
            content_type=create_task_request.content_type,
            content=create_task_request.content,
            display_order=display_order,
            estimated_time=create_task_request.estimated_time,
            created_by=current_author.email,
        )

    saved_task = save_task(db=db,new_task=new_task)

    return TaskDTO(
        id=saved_task.id,
        title=saved_task.title,
        content_type=saved_task.content_type,
        content=saved_task.content,
        display_order=saved_task.display_order,
        estimated_time=saved_task.estimated_time,
    )

async def change_task_day_service(token: str, task_id: UUID, update_task_request: UpdateTaskDayRequest) -> UpdatedTaskDayResponse:
    validate_and_extract_author_details(token=token)

    with SessionLocal() as db:
        display_order = _get_max_display_order(plan_item_id=update_task_request.target_day_id) + 1

        targeted_day = get_plan_item_by_id(db=db, day_id=update_task_request.target_day_id)
        if targeted_day.id == update_task_request.target_day_id:
            raise HTTPException(status_code=404, detail=ResponseError(error=BAD_REQUEST, message=TASK_SAME_DAY_NOT_ALLOWED).model_dump())
        if not targeted_day:
            raise HTTPException(status_code=404, detail=ResponseError(error=BAD_REQUEST, message=PLAN_DAY_NOT_FOUND).model_dump())

        task = update_task_day(db=db, task_id=task_id, target_day_id=update_task_request.target_day_id, display_order=display_order)

        return UpdatedTaskDayResponse(
            task_id=task.id, 
            day_id=task.plan_item_id, 
            display_order=task.display_order, 
            estimated_time=task.estimated_time,
            title=task.title,
        )