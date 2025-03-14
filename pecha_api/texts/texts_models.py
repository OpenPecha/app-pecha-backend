import uuid
from typing import Dict, List

from pydantic import BaseModel, Field

class Mapping(BaseModel):
    text_id: str
    segments: List[str]

class Segment(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    text_id: str
    content: str
    mapping: List[Mapping]

    class Settings:
        collection = "segments"

class Text(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    titles: Dict[str, str] = Field(default_factory={})
    language: str
    is_published: bool
    created_date: str
    updated_date: str
    published_date: str
    published_by: str
    type: str
    categories: List[str]

    class Settings:
        collection = "texts"