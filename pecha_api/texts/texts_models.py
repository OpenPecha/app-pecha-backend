import uuid
from uuid import UUID
from typing import List, Optional

from .texts_response_models import TextDetailsRequest, Section

from pydantic import Field
from beanie import Document

class TableOfContent(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    text_id: str
    sections: List[Section]

    class Settings:
        collection = "table_of_contents"
    
    @classmethod
    async def get_table_of_contents_by_text_id(cls, text_id: str) -> List["TableOfContent"]: # this methods is getting all the available table of content for a text
        return await cls.find(cls.text_id == text_id).to_list()
    
    @classmethod
    async def get_sections_count(cls, content_id: str) -> int:
        return await cls.find_one(cls.id == UUID(content_id)).sections.count()
    
    @classmethod
    async def get_table_of_content_by_content_id(cls, content_id: str, skip: int, limit: int) -> Optional["TableOfContent"]:
        contents = await cls.find_one(cls.id == UUID(content_id))
        if contents:
            contents.sections.sort(key=lambda section: section.section_number)
            if (skip * limit) > len(contents.sections):
                return None
            contents.sections = contents.sections[skip * limit:skip+limit]
        return contents


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
    async def get_text(cls, text_id: str) -> Optional["Text"]:
        try:
            text_uuid = UUID(text_id)
        except ValueError:
            return None
        return await cls.find_one(cls.id == text_uuid)
    
    @classmethod
    async def get_texts_by_ids(cls, text_ids: List[str]) -> List["Text"]:
        # Use the correct MongoDB query syntax
        return await cls.find({"_id": {"$in": text_ids}}).to_list()

    @classmethod
    async def check_exists(cls, text_id: uuid.UUID) -> bool:
        text = await cls.find_one(cls.id == text_id)
        return text is not None  # True if exists, False otherwise

    @classmethod
    async def exists_all(cls, text_ids: List[UUID], batch_size: int = 100) -> bool:
        for i in range(0, len(text_ids), batch_size):
            batch_ids = text_ids[i: i + batch_size]
            found_texts = await cls.find({"_id": {"$in": batch_ids}}).to_list()

            found_ids = {text.id for text in found_texts}

            # If any ID from the current batch is missing, stop early
            if len(found_ids) < len(batch_ids):
                return False  # One or more IDs are missing
        return True  # All IDs exist
    
    @classmethod
    async def get_texts_by_term_id(cls, term_id: str, skip: int, limit: int) -> List["Text"]:
        query = {"categories": term_id, "type": {"$ne": "version"}}
        texts = (
            await cls.find(query)
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return texts
    
    @classmethod
    async def get_versions_by_text_id(cls, text_id: str, skip: int, limit: int) -> List["Text"]:
        query = {"parent_id": text_id, "type": "version"}
        texts = (
            await cls.find(query)
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return texts

