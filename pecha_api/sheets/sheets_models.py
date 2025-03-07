import uuid
from typing import Dict, List, Union

from beanie import PydanticObjectId, Document
from pydantic import BaseModel, Field

class Source(BaseModel):
    position: int
    text_ref: str
    text: Dict[str, str]

class Text(BaseModel):
    position: int
    text: str

class Media(BaseModel):
    position: int
    media_type: str
    media: str

class Like(BaseModel):
    username: str
    name: str

class Sheet(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    titles: Dict[str, str] = Field(default_factory=dict)
    summaries: Dict[str, str] = Field(default_factory=dict)
    source: List[Union[Source, Text, Media]] = Field(default_factory=list)
    publisher_id: str
    creation_date: str
    modified_date: str
    published_date: str
    published_time: int
    views: str
    likes: List[Like] = Field(default_factory=list)
    collection: List[str] = Field(default_factory=list)
    topic_id: List[str] = Field(default_factory=list)

    class Settings:
        name = "sheets"  # Collection name in MongoDB