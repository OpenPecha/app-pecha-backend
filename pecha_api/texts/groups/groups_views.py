from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import APIRouter, Depends, Query
from typing import Annotated
from starlette import status

from .groups_response_models import (
    CreateGroupRequest,
)

oauth2_scheme = HTTPBearer()
group_router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)

@group_router.post("", status_code=status.HTTP_201_CREATED)
async def create_group(
    create_group_request: CreateGroupRequest,
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
):
    return await create_new_group(
        create_group_request=create_group_request,
        token=authentication_credential.credentials
    )
