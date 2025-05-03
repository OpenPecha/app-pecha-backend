import uuid
from beanie import Document
from uuid import UUID

from .groups_response_models import (
    GroupDTO
)

class Group(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    type: str

    class Settings:
        collection = "groups"
    
    @classmethod
    async def check_exists(cls, group_id: UUID) -> bool:
        group = await cls.find_one(cls.id == group_id)
        return group is not None

    @classmethod
    async def get_group_by_id(cls, group_id: UUID):
        return await cls.find_one(cls.id == group_id)
