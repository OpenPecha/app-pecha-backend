

from .groups_models import Group
from .groups_response_models import (
    CreateGroupRequest,
    GroupDTO
)

async def get_group_by_id(group_id: str) -> GroupDTO:
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
