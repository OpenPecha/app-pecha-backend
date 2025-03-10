import uuid
from typing import Dict, List, Union

from beanie import PydanticObjectId, Document
from pydantic import BaseModel, Field

class Source(BaseModel):
    position: int
    type: str
    text_ref: str
    text: Dict[str, str]

class Text(BaseModel):
    position: int
    text: str

class Media(BaseModel):
    position: int
    type : str
    media_type: str
    media: str

class Like(BaseModel):
    username: str
    name: str

class Sheet(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    titles: str 
    summaries: str
    source: List[Union[Source, Text, Media]] = Field(default_factory=list)
    publisher_id: str
    creation_date: str #UTC date with date and time
    modified_date: str #UTC date with date and time
    published_date: int #epoch time
    views: int
    likes: List[Like] = Field(default_factory=list)
    collection: List[str] = Field(default_factory=list)
    topic_id: List[str] = Field(default_factory=list)
    sheetLanguage: str
    

    class Settings:
        name = "Sheets"  # Collection name in MongoDB

    @classmethod
    async def get_sheets_by_user_id(cls, user_id: str, skip: int, limit: int):
        query = {"publisher_id": user_id}
        return await cls.find(query).skip(skip).limit(limit).to_list()