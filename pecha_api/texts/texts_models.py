import uuid
from typing import Dict, List, Optional

from pydantic import Field
from beanie import Document

class Text(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    language: str
    parent_id: Optional[str] = None
    is_published: bool
    created_date: str
    updated_date: str
    published_date: str
    published_by: str
    type: str
    categories: List[str]

    class Settings:
        collection = "texts"