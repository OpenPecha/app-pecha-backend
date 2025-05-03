from ...users.users_service import verify_admin_access
from ...error_contants import ErrorConstants
from fastapi import HTTPException
from starlette import status

from .groups_repository import (
    create_group
)

from .groups_response_models import (
    CreateGroupRequest,
    GroupDTO
)

async def get_group_details(group_id: str) -> GroupDTO:
    return await get_group_by_id(group_id=group_id)

async def create_new_group(
    create_group_request: CreateGroupRequest,
    token: str
) -> GroupDTO:
    is_admin = await verify_admin_access(token=token)
    if not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.ADMIN_ERROR_MESSAGE)
    return await create_group(
        create_group_request=create_group_request
    )