import uuid
from uuid import UUID
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
    
    @classmethod
    async def get_text(cls, text_id: str):
        try:
            text_uuid = UUID(text_id)
        except ValueError:
            return None
        
        return await cls.find_one(cls.id == text_uuid)