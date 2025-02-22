import uuid
from typing import Dict, Optional, List

from beanie import PydanticObjectId, Document
from pydantic import Field




class Topic(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    titles: Dict[str, str]
    parent_id: Optional[PydanticObjectId] = None
    default_language: str

    class Settings:
        # Define the collection name in MongoDB
        collection = "topics"

    class Config:
        # Config for Pydantic to allow alias to be used
        populate_by_name = True
    

    @classmethod
    async def get_children_by_id(cls, parent_id: PydanticObjectId, search: Optional[str], skip: int, limit: int) -> List["Topic"]:

        query = {"parent_id": parent_id}

        if search:
            query["title"] = {"$regex": f"^{search}", "$options": "i"}

        return await cls.find(query).skip(skip).limit(limit).to_list()

    @classmethod
    async def count_children(cls, parent_id: PydanticObjectId) -> int:
        """
        Count total number of children for a given parent
        """
        return await cls.find({"parent_id": parent_id}).count()