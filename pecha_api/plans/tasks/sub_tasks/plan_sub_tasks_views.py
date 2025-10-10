from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from uuid import UUID
from starlette import status

from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_response_model import SubTaskRequest, SubTaskResponse
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services import create_new_sub_tasks

sub_tasks_router = APIRouter(
    prefix="/cms/plan",
    tags=["Sub Tasks"]
)

oauth2_scheme = HTTPBearer()

@sub_tasks_router.post("/task/{task_id}/sub-tasks", status_code=status.HTTP_201_CREATED, response_model=SubTaskResponse)
async def create_sub_tasks(
        authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
        create_task_request: SubTaskRequest,
        task_id: UUID,
):
    return await create_new_sub_tasks(
        token=authentication_credential.credentials,
        create_task_request=create_task_request,
        task_id=task_id,
    )