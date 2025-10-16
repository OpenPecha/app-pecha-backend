from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from uuid import UUID
from starlette import status

from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_response_model import SubTaskRequest, SubTaskResponse, UpdateSubTaskRequest, UpdateSubTaskResponse
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_services import create_new_sub_tasks, update_sub_task_by_task_id

sub_tasks_router = APIRouter(
    prefix="/cms/sub-tasks",
    tags=["Sub Tasks"]
)

oauth2_scheme = HTTPBearer()

@sub_tasks_router.post("", status_code=status.HTTP_201_CREATED, response_model=SubTaskResponse)
async def create_sub_tasks(
        authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
        create_task_request: SubTaskRequest,
):
    return await create_new_sub_tasks(
        token=authentication_credential.credentials,
        create_task_request=create_task_request,
    )

@sub_tasks_router.put("", status_code=status.HTTP_200_OK, response_model=UpdateSubTaskResponse)
async def update_sub_task(
        authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
        update_sub_task_request: UpdateSubTaskRequest,
):
    return await update_sub_task_by_task_id(
        token=authentication_credential.credentials,
        update_sub_task_request=update_sub_task_request,
    )