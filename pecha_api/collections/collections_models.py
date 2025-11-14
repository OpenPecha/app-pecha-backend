from codecs import strict_errors
from typing import Dict, List, Optional

from beanie import Document, PydanticObjectId
from pydantic import  Field

class Collection(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    slug: str
    titles: Dict[str, str]  # Dictionary with language_id as key and title as value
    descriptions: Dict[str,str] = Field(default=dict)
    parent_id: Optional[str] = None
    has_sub_child: bool = False

    class Settings:
        # Define the collection name in MongoDB
        collection = "collections"

    class Config:
        # Config for Pydantic to allow alias to be used
        populate_by_name = True

    # Define indexes directly within the model
    class __Indexes__:
        # Create a unique index on the `slug` field
        indexes = [("slug", 1)]

    @classmethod
    async def get_by_id(cls, parent_id: str) -> "Collection":
        return await cls.find({"parent_id": parent_id})
    
    @classmethod
    async def get_by_slug(cls, slug: str) -> "Collection":
        return await cls.find_one({"slug": slug})

    @classmethod
    async def get_children_by_id(cls, parent_id: str,skip: int, limit: int) -> List["Collection"]:
        return await cls.find({"parent_id": parent_id}).skip(skip).limit(limit).to_list()
    
    @classmethod
    async def get_all_children_by_id(cls, parent_id: str) -> List["Collection"]:
        return await cls.find({"parent_id": parent_id}).to_list()
    
    @classmethod
    async def count_children(cls, parent_id: strict_errors) -> int:
        """
        Count total number of children for a given parent
        """
        return await cls.find({"parent_id": parent_id}).count()
