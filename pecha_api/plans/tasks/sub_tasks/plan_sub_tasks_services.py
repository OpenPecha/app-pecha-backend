from typing import List
from uuid import UUID

from fastapi import HTTPException
from starlette import status

from pecha_api.db.database import SessionLocal
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.authors.plan_authors_service import validate_and_extract_author_details
from pecha_api.plans.response_message import BAD_REQUEST, FORBIDDEN, UNAUTHORIZED_TASK_ACCESS
from pecha_api.plans.tasks.plan_tasks_repository import get_task_by_id
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_models import PlanSubTask
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_repository import (
    get_max_display_order_for_sub_task,
    save_sub_tasks_bulk,
    get_sub_tasks_by_task_id,
    delete_sub_tasks_bulk,
    update_sub_tasks_bulk,
    get_sub_task_by_id,
    update_sub_task_order,
    update_sub_tasks
)

from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_response_model import (
    SubTaskDTO,
    SubTaskRequest,
    SubTaskResponse,
    UpdateSubTaskRequest,
    SubTaskOrderRequest,
    SubTaskOrderResponse
)
from pecha_api.error_contants import ErrorConstants
from pecha_api.plans.response_message import SUBTASK_ORDER_FAILED

async def create_new_sub_tasks(token: str, create_task_request: SubTaskRequest) -> SubTaskResponse:
    current_author = validate_and_extract_author_details(token=token)

    with SessionLocal() as db:
        task = get_task_by_id(db=db, task_id=create_task_request.task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ResponseError(error=BAD_REQUEST, message=ErrorConstants.TASK_NOT_FOUND).model_dump(),
            )

        next_display_order = get_max_display_order_for_sub_task(db=db, task_id=create_task_request.task_id) + 1

        new_sub_tasks: List[PlanSubTask] = []
        for index, sub in enumerate(create_task_request.sub_tasks, start=0):
            
            new_sub_tasks.append(
                PlanSubTask(
                    task_id=create_task_request.task_id,
                    content_type=sub.content_type,
                    content=sub.content,
                    display_order=next_display_order + index,
                    created_by=current_author.email,
                )
            )

        saved_sub_tasks = save_sub_tasks_bulk(db=db, sub_tasks=new_sub_tasks)
        created_sub_tasks=[
                SubTaskDTO(
                    id=item.id,
                    content_type=item.content_type,
                    content=item.content,
                    display_order=item.display_order,
                )
                for item in saved_sub_tasks
            ]
        return SubTaskResponse(
            sub_tasks=created_sub_tasks,
        )

async def update_sub_task_by_task_id(token: str, update_sub_task_request: UpdateSubTaskRequest) -> None:
    current_author = validate_and_extract_author_details(token=token)

    with SessionLocal() as db:
        task = get_task_by_id(db=db, task_id=update_sub_task_request.task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseError(error=BAD_REQUEST, message=ErrorConstants.TASK_NOT_FOUND).model_dump())

        if task.created_by != current_author.email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ResponseError(error=FORBIDDEN, message=UNAUTHORIZED_TASK_ACCESS).model_dump())

        existing_sub_tasks_to_update: List[SubTaskDTO] = [
            subtask for subtask in update_sub_task_request.sub_tasks if subtask.id is not None
        ]

        new_sub_tasks_to_create: List[PlanSubTask] = [
            PlanSubTask(
                task_id=update_sub_task_request.task_id,
                content_type=subtask.content_type,
                content=subtask.content,
                display_order=subtask.display_order,
                created_by=current_author.email,
            )
            for subtask in update_sub_task_request.sub_tasks
            if subtask.id is None
        ]

        # Compute deletions BEFORE creating new sub tasks to avoid deleting freshly created records
        existing_in_db = get_sub_tasks_by_task_id(db=db, task_id=update_sub_task_request.task_id)
        existing_ids_in_db = [sub_task.id for sub_task in existing_in_db]
        requested_existing_ids = [sub_task.id for sub_task in existing_sub_tasks_to_update]
        sub_tasks_ids_to_delete = [id for id in existing_ids_in_db if id not in requested_existing_ids]

        delete_sub_tasks_bulk(db=db, sub_tasks_ids=sub_tasks_ids_to_delete)

        # Update only existing sub tasks
        update_sub_tasks_bulk(db=db, sub_tasks=existing_sub_tasks_to_update)

        # Finally, create new sub tasks
        if new_sub_tasks_to_create:
            save_sub_tasks_bulk(db=db, sub_tasks=new_sub_tasks_to_create)


async def change_subtask_order_service(token: str, sub_task_id: UUID, update_subtask_order_request: SubTaskOrderRequest) -> SubTaskOrderResponse:
    
    current_author = validate_and_extract_author_details(token=token)
    
    with SessionLocal() as db:
        
        current_subtask = get_sub_task_by_id(db=db, sub_task_id=sub_task_id)
        task = get_task_by_id(db=db, task_id=current_subtask.task_id)
        
        if task.created_by != current_author.email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ResponseError(error=FORBIDDEN, message=UNAUTHORIZED_TASK_ACCESS).model_dump())
        
        current_display_order = current_subtask.display_order
        target_display_order = update_subtask_order_request.target_order
        task_id = current_subtask.task_id
        
        all_subtasks = get_sub_tasks_by_task_id(db=db, task_id=task_id)
        
        subtasks_to_shift = []
        if current_display_order < target_display_order:
            subtasks_to_shift = [
                subtask for subtask in all_subtasks 
                if subtask.id != sub_task_id and current_display_order < subtask.display_order <= target_display_order
            ]
            order_adjustment = -1
        else:
            subtasks_to_shift = [
                subtask for subtask in all_subtasks 
                if subtask.id != sub_task_id and target_display_order <= subtask.display_order < current_display_order
            ]
            order_adjustment = 1
        
        if subtasks_to_shift:
            for subtask in subtasks_to_shift:
                subtask.display_order += order_adjustment
            update_sub_tasks(db)
        
        current_subtask.display_order = target_display_order
        updated_subtask = update_sub_task_order(db=db, sub_task=current_subtask)
        
        if not updated_subtask:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseError(error=BAD_REQUEST, message=SUBTASK_ORDER_FAILED).model_dump())
        
        return SubTaskOrderResponse(
            sub_task_id=updated_subtask.id,
            display_order=updated_subtask.display_order
        )