from ...users.users_service import verify_admin_access
from ...error_contants import ErrorConstants
from fastapi import HTTPException
from starlette import status
from uuid import UUID
from typing import Dict, List
import logging

from .groups_repository import (
    create_group,
    check_group_exists,
    get_group_by_id,
    get_groups_by_ids
)

from .groups_response_models import (
    CreateGroupRequest,
    GroupDTO
)

async def validate_group_exists(group_id: str) -> bool:
    is_exists = False
    try:
        uuid_group_id = UUID(group_id)
        is_exists = await check_group_exists(group_id=uuid_group_id)
        if not is_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorConstants.GROUP_NOT_FOUND_MESSAGE
            )
        return is_exists
    except ValueError:
        logging.error(f"Invalid group_id provided: {group_id}")
        return False
    
async def get_groups_by_list_of_ids(group_ids: List[str]) -> Dict[str, GroupDTO]:
    return await get_groups_by_ids(group_ids=group_ids)

async def get_group_details(group_id: str) -> GroupDTO:
    try:
        uuid_group_id = UUID(group_id)
        return await get_group_by_id(group_id=uuid_group_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorConstants.INVALID_GROUP_ID_MESSAGE
        )

async def create_new_group(
    create_group_request: CreateGroupRequest,
    token: str
) -> GroupDTO:
    is_admin = verify_admin_access(token=token)
    if not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.ADMIN_ERROR_MESSAGE)
    return await create_group(
        create_group_request=create_group_request
    )