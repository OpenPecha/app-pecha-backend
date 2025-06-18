import uuid
from typing import Dict, List, Union, Optional

from beanie import PydanticObjectId, Document
from pydantic import BaseModel, Field


class Source(BaseModel):
    position: int
    source_segment_id: str
    translation_segment_id: Optional[str] = None

class Text(BaseModel):
    position: int
    segment_id: str

class Media(BaseModel):
    position: int
    media_type: str
    media_url: str

class Like(BaseModel):
    username: str
    name: str

class Sheet(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    titles: str 
    sources: List[Union[Source, Text, Media]] = Field(default_factory=list)
    publisher_id: str
    isPublic: bool = False
    creation_date: str #UTC date with date and time
    modified_date: str #UTC date with date and time
    published_date: int #epoch time
    views: int
    likes: List[Like] = Field(default_factory=list)
    collection: List[str] = Field(default_factory=list)
    

    class Settings:
        name = "Sheets"  # Collection name in MongoDB

    @classmethod
    async def get_sheets_by_user_id(cls, user_id: str, skip: int, limit: int):
        query = {"publisher_id": user_id}
        return await cls.find(query).skip(skip).limit(limit).to_list()