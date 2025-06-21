from typing import List, Optional
import uuid
from pydantic import BaseModel, Field
from beanie import Document

from .segments_enum import SegmentType

class Mapping(BaseModel):
    text_id: str
    segments: List[str]


class Segment(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    text_id: str
    content: str
    mapping: Optional[List[Mapping]] = None
    type: SegmentType

    class Settings:
        collection = "segments"
        indexes = [
            "mapping.segments"  # Index for faster lookup of segment IDs within mapping arrays
        ]

    @classmethod
    async def get_segment_by_id(cls, segment_id: str) -> Optional["Segment"]:
        return await cls.find_one(cls.id == uuid.UUID(segment_id))

    @classmethod
    async def get_segment_by_id_and_text_id(cls, segment_id: uuid.UUID, text_id: str) -> Optional["Segment"]:
        return await cls.find_one(cls.id == segment_id, cls.text_id == text_id)

    @classmethod
    async def get_segments_by_text_id(cls, text_id: str) -> List["Segment"]:
        return await cls.find(cls.text_id == text_id).to_list()

    @classmethod
    async def check_exists(cls, segment_id: uuid.UUID) -> bool:
        segment = await cls.find_one(cls.id == segment_id)
        return segment is not None

    @classmethod
    async def exists_all(cls, segment_ids: List[uuid.UUID], batch_size: int = 100) -> bool:
        for i in range(0, len(segment_ids), batch_size):
            batch_ids = segment_ids[i: i + batch_size]
            found_segments = await cls.find({"_id": {"$in": batch_ids}}).to_list()

            found_ids = {text.id for text in found_segments}
            # If any ID from the current batch is missing, stop early
            if len(found_ids) < len(batch_ids):
                return False
        return True  # All IDs exist

    @classmethod
    async def get_segments_by_ids(cls, segment_ids: List[str]) -> List["Segment"]:
        segment_ids = [uuid.UUID(segment_id) for segment_id in segment_ids]
        return await cls.find({"_id": {"$in": segment_ids}}).to_list(length=len(segment_ids))
    
    @classmethod
    async def get_related_mapped_segments(cls, parent_segment_id: str) -> List["Segment"]:
        # Find segments where:
        # 1. There exists a mapping object with text_id matching parent_text_id
        # 2. Within that same mapping object, segments list contains parent_segment_id
        query = {
            "mapping": {
                "$elemMatch": {
                    "segments": {"$in": [parent_segment_id]}
                }
            }
        }
        return await cls.find(query).to_list()
    
    @classmethod
    async def delete_segment_by_text_id(cls, text_id: str):
        return await cls.delete_many(cls.text_id == text_id)