from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import APIRouter, Depends, Query
from typing import Annotated
from uuid import UUID
from starlette import status

from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO
from pecha_api.plans.tasks.plan_tasks_services import create_new_task, delete_task_by_id

oauth2_scheme = HTTPBearer()
# Create router for plan endpoints
plans_router = APIRouter(
    prefix="/cms/plan",
    tags=["Task"]
)


@plans_router.post("/{plan_id}/day/{day_id}/tasks", status_code=status.HTTP_201_CREATED, response_model=TaskDTO)
async def create_task(
        authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
        create_task_request: CreateTaskRequest,
        plan_id: UUID,
        day_id: UUID,
):
    new_task: TaskDTO = await create_new_task(
        token=authentication_credential.credentials,
        create_task_request=create_task_request,
        plan_id=plan_id,
        day_id=day_id,
    )
    return new_task

@plans_router.delete("/{plan_id}/day/{day_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    plan_id: UUID,
    day_id: UUID,
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
):
    await delete_task_by_id(
        task_id=task_id,
        token=authentication_credential.credentials
    )   