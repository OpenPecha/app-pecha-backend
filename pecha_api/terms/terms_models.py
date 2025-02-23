from typing import Dict, List, Optional

from beanie import Document, PydanticObjectId
from pydantic import  Field

class Term(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    slug: str
    titles: Dict[str, str]  # Dictionary with language_id as key and title as value
    descriptions: Dict[str,str] = Field(default=dict)
    parent_id: Optional[PydanticObjectId] = None
    has_sub_child: bool = False

    class Settings:
        # Define the collection name in MongoDB
        collection = "terms"

    class Config:
        # Config for Pydantic to allow alias to be used
        populate_by_name = True

    # Define indexes directly within the model
    class __Indexes__:
        # Create a unique index on the `slug` field
        indexes = [("slug", 1)]

    @classmethod
    async def get_children_by_id(cls, parent_id: PydanticObjectId,skip: int, limit: int) -> List["Term"]:
        return await cls.find({"parent_id": parent_id}).skip(skip).limit(limit).to_list()

    @classmethod
    async def count_children(cls, parent_id: PydanticObjectId) -> int:
        """
        Count total number of children for a given parent
        """
        return await cls.find({"parent_id": parent_id}).count()
