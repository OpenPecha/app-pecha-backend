import uuid
from typing import Dict, Optional, List

from beanie import PydanticObjectId, Document
from pydantic import Field




class Topic(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    titles: Dict[str, str]
    parent_id: Optional[PydanticObjectId] = None
    default_language: str
    has_sub_child: bool = False

    class Settings:
        # Define the collection name in MongoDB
        collection = "topics"

    class Config:
        # Config for Pydantic to allow alias to be used
        populate_by_name = True
    

    @classmethod
    async def get_children_by_id(cls, parent_id: PydanticObjectId, search: Optional[str], heirarchy: Optional[bool], language: Optional[str], skip: int, limit: int) -> List["Topic"]:

        query = {}
        if search:
            if parent_id:
                query["parent_id"] = parent_id
                query[f"titles.{language}"] = {"$regex": f"^{search}", "$options": "i"}
            elif heirarchy:
                query["parent_id"] = {"$ne": None}
                query[f"titles.{language}"] = {"$regex": f"^{search}", "$options": "i"}
            else:
                query[f"titles.{language}"] = {"$regex": f"^{search}", "$options": "i"}
        elif parent_id:
            query["parent_id"] = parent_id
        elif heirarchy:
                query["parent_id"] = None


        return await cls.find(query).skip(skip).limit(limit).to_list()

    @classmethod
    async def count_children(cls, parent_id: PydanticObjectId) -> int:
        """
        Count total number of children for a given parent
        """
        return await cls.find({"parent_id": parent_id}).count()