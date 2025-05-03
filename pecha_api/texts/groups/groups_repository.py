from uuid import UUID
from beanie.exceptions import CollectionWasNotInitialized
import logging
from typing import List
from ...constants import Constants

from .groups_models import Group
from .groups_response_models import (
    CreateGroupRequest,
    GroupDTO
)

async def check_group_exists(group_id: UUID) -> bool:
    try:
        is_group_exists = await Group.check_exists(group_id=group_id)
        return is_group_exists
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return False

async def get_group_by_id(group_id: UUID) -> GroupDTO:
    group = await Group.get_group_by_id(group_id=group_id)
    return GroupDTO(
        id=str(group.id),
        type=group.type
    )

async def create_group(
    create_group_request: CreateGroupRequest
) -> GroupDTO:

    group = Group(
        type=create_group_request.type
    )

    await group.insert()

    return GroupDTO(
        id=str(group.id),
        type=group.type
    )
