from typing import List
from uuid import UUID

from fastapi import HTTPException
from starlette import status

from pecha_api.db.database import SessionLocal
from pecha_api.plans.auth.plan_auth_models import ResponseError
from pecha_api.plans.authors.plan_authors_service import validate_and_extract_author_details
from pecha_api.plans.plans_enums import ContentType
from pecha_api.plans.response_message import BAD_REQUEST, FORBIDDEN, UNAUTHORIZED_TASK_ACCESS
from pecha_api.plans.tasks.plan_tasks_repository import get_task_by_id
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_models import PlanSubTask
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_repository import (
    get_max_display_order_for_sub_task,
    save_sub_tasks_bulk,
    get_sub_tasks_by_task_id,
    delete_sub_tasks_bulk,
    update_sub_tasks_bulk
)

from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_response_model import (
    SubTaskDTO,
    SubTaskRequest,
    SubTaskResponse,
    UpdateSubTaskRequest,
    UpdateSubTaskResponse,
)
from pecha_api.error_contants import ErrorConstants

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

async def update_sub_task_by_task_id(token: str, update_sub_task_request: UpdateSubTaskRequest) -> UpdateSubTaskResponse:
    current_author = validate_and_extract_author_details(token=token)

    with SessionLocal() as db:
        task = get_task_by_id(db=db, task_id=update_sub_task_request.task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ResponseError(error=BAD_REQUEST, message=ErrorConstants.TASK_NOT_FOUND).model_dump())

        if task.created_by != current_author.email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ResponseError(error=FORBIDDEN, message=UNAUTHORIZED_TASK_ACCESS).model_dump())

    
        sub_tasks = get_sub_tasks_by_task_id(db=db, task_id=update_sub_task_request.task_id)
        sub_tasks_ids = [sub_task.id for sub_task in sub_tasks]
        requested_sub_tasks_ids = [sub_task.id for sub_task in update_sub_task_request.sub_tasks]
        sub_tasks_ids_to_delete = [id for id in sub_tasks_ids if id not in requested_sub_tasks_ids]

        delete_sub_tasks_bulk(db=db, sub_tasks_ids=sub_tasks_ids_to_delete)

        update_sub_tasks_bulk(db=db, sub_tasks=sub_tasks_to_update)


