from pecha_api.plans.tasks.plan_tasks_repository import save_task, get_task_by_id, delete_task, update_task_day, update_task_title, update_task_order, shift_tasks_order, get_tasks_by_plan_item_id
from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO, UpdateTaskDayRequest, UpdatedTaskDayResponse, GetTaskResponse, UpdateTaskTitleRequest, UpdateTaskTitleResponse, ContentAndImageUrl, UpdateTaskOrderRequest, UpdatedTaskOrderResponse
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_response_model import SubTaskDTO
from pecha_api.plans.authors.plan_authors_service import validate_and_extract_author_details
from uuid import UUID
from fastapi import HTTPException
from pecha_api.db.database import SessionLocal
from pecha_api.plans.items.plan_items_repository import get_plan_item, get_plan_item_by_id
from pecha_api.plans.tasks.plan_tasks_models import PlanTask
from sqlalchemy import func
from fastapi import HTTPException
from starlette import status
from pecha_api.plans.response_message import PLAN_DAY_NOT_FOUND, BAD_REQUEST, FORBIDDEN, UNAUTHORIZED_TASK_DELETE, UNAUTHORIZED_TASK_ACCESS, TASK_ORDER_UPDATE_FAIL
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.uploads.S3_utils import generate_presigned_access_url
from pecha_api.config import get
from pecha_api.plans.plans_enums import ContentType

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
        
async def change_task_day_service(token: str, task_id: UUID, update_task_request: UpdateTaskDayRequest) -> UpdatedTaskDayResponse:
    validate_and_extract_author_details(token=token)

    with SessionLocal() as db:
        display_order = _get_max_display_order(plan_item_id=update_task_request.target_day_id) + 1

        targeted_day = get_plan_item_by_id(db=db, day_id=update_task_request.target_day_id)

        if not targeted_day:
            raise HTTPException(status_code=404, detail=ResponseError(error=BAD_REQUEST, message=PLAN_DAY_NOT_FOUND).model_dump())

        task = update_task_day(
            db=db, 
            task_id=task_id, 
            target_day_id=update_task_request.target_day_id, 
            display_order=display_order
        )

        return UpdatedTaskDayResponse(
            task_id=task.id, 
            day_id=task.plan_item_id, 
            display_order=task.display_order, 
            estimated_time=task.estimated_time,
            title=task.title,
        )

async def update_task_title_service(token: str, task_id: UUID, update_request: UpdateTaskTitleRequest) -> UpdateTaskTitleResponse:
    current_author = validate_and_extract_author_details(token=token)
    
    with SessionLocal() as db:
        task = get_task_by_id(db=db, task_id=task_id)
        
        if task.created_by != current_author.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=ResponseError(error=FORBIDDEN, message=UNAUTHORIZED_TASK_ACCESS).model_dump()
            )
        
        updated_task = update_task_title(db=db, task_id=task_id, title=update_request.title)
        
        return UpdateTaskTitleResponse(
            task_id=updated_task.id,
            title=updated_task.title
        )

async def change_task_order_service(token: str, task_id: UUID, update_task_order_request: UpdateTaskOrderRequest) -> UpdatedTaskOrderResponse:
    current_author = validate_and_extract_author_details(token=token)

    with SessionLocal() as db:
        current_task = get_task_by_id(db=db, task_id=task_id)

        if current_task.created_by != current_author.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=ResponseError(error=FORBIDDEN, message=UNAUTHORIZED_TASK_ACCESS).model_dump()
            )
        
        current_display_order = current_task.display_order
        plan_item_id = current_task.plan_item_id
        target_display_order = update_task_order_request.target_order
        
        all_tasks = get_tasks_by_plan_item_id(db=db, plan_item_id=plan_item_id)
        
        tasks_to_shift = []
        if current_display_order < target_display_order:
            tasks_to_shift = [
                task for task in all_tasks 
                if task.id != task_id and current_display_order < task.display_order <= target_display_order
            ]
            order_adjustment = -1
        else:
            tasks_to_shift = [
                task for task in all_tasks 
                if task.id != task_id and target_display_order <= task.display_order < current_display_order
            ]
            order_adjustment = 1
        
        if tasks_to_shift:
            shift_tasks_order(db=db, tasks_to_update=tasks_to_shift, order_adjustment=order_adjustment)
        
        update_current_task_display_order = update_task_order(
            db=db, 
            task_id=task_id, 
            display_order=target_display_order
        )

        if not update_current_task_display_order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=ResponseError(
                    error=BAD_REQUEST, 
                    message=TASK_ORDER_UPDATE_FAIL
                ).model_dump()
            )

        return UpdatedTaskOrderResponse(
            task_id=update_current_task_display_order.id,
            display_order=update_current_task_display_order.display_order,
        )


async def get_task_subtasks_service(task_id: UUID, token: str) -> GetTaskResponse:
    current_user = validate_and_extract_author_details(token=token)

    with SessionLocal() as db:
        task = get_task_by_id(db=db, task_id=task_id)

        if task.created_by != current_user.email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ResponseError(error=FORBIDDEN, message=UNAUTHORIZED_TASK_ACCESS).model_dump())
        
        subtasks_dto = []
        for sub_task in task.sub_tasks:
            content_and_image_url = _generate_image_url_content_type(
                content_type=sub_task.content_type,
                content=sub_task.content,
            )
            subtasks_dto.append(
                SubTaskDTO(
                    id=sub_task.id,
                    content_type=sub_task.content_type,
                    content=content_and_image_url.content,
                    image_url=content_and_image_url.image_url,
                    display_order=sub_task.display_order,
                )
            )

        return GetTaskResponse(
            id=task.id,
            title=task.title,
            display_order=task.display_order,
            estimated_time=task.estimated_time,
            subtasks=subtasks_dto,
        )

def _generate_image_url_content_type(content_type: str, content: str) -> ContentAndImageUrl:
    if content_type == ContentType.IMAGE:
        presigned_url = generate_presigned_access_url(
            bucket_name=get("AWS_BUCKET_NAME"), s3_key=content
        )
        return ContentAndImageUrl(content=presigned_url, image_url=content)
    return ContentAndImageUrl(content=content, image_url=None)
