from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import APIRouter, Depends, Query
from typing import Annotated
from uuid import UUID
from starlette import status

from pecha_api.plans.tasks.plan_tasks_response_model import CreateTaskRequest, TaskDTO
from pecha_api.plans.tasks.plan_tasks_services import create_new_task

oauth2_scheme = HTTPBearer()
# Create router for plan endpoints
plans_router = APIRouter(
    prefix="/cms/plan",
    tags=["Task"]
)


@plans_router.post("/{plan_id}/day/{day_id}", status_code=status.HTTP_200_OK, response_model=TaskDTO)
async def create_task(
        authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
        create_task_request: CreateTaskRequest,
        plan_id: str,
        day_id: str,
):
    return await create_new_task(
        token=authentication_credential.credentials,
        create_task_request=create_task_request,
        plan_id=plan_id,
        day_id=day_id,
    )
