from typing import List
import uuid
from pydantic import BaseModel, Field
from beanie import Document


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

    @classmethod
    async def get_segment_by_id(cls, segment_id: str):
        return await cls.find_one(cls.id == uuid.UUID(segment_id))

    @classmethod
    async def get_segment_by_id_and_text_id(cls, segment_id: uuid.UUID, text_id: str):
        return await cls.find_one(cls.id == segment_id, cls.text_id == text_id)

    @classmethod
    async def check_exists(cls, segment_id: uuid.UUID):
        segment = await cls.find_one(cls.id == segment_id)
        return segment is not None

    @classmethod
    async def exists_all(cls, segment_ids: List[uuid.UUID], batch_size: int = 100):
        for i in range(0, len(segment_ids), batch_size):
            batch_ids = segment_ids[i: i + batch_size]
            found_segments = await cls.find({"_id": {"$in": batch_ids}}).to_list()

            found_ids = {text.id for text in found_segments}
            # If any ID from the current batch is missing, stop early
            if len(found_ids) < len(batch_ids):
                return False
        return True  # All IDs exist

    @classmethod
    async def get_segments(cls, segment_ids: List[str]):
        segment_ids = [uuid.UUID(segment_id) for segment_id in segment_ids]
        return await cls.find({"_id": {"$in": segment_ids}}).to_list(length=len(segment_ids))
    
    @classmethod
    async def get_related_mapped_segments(cls, child_text_id: str, parent_text_id: str, parent_segment_id: str):
        # Find segments where:
        # 1. There exists a mapping object with text_id matching parent_text_id
        # 2. Within that same mapping object, segments list contains parent_segment_id
        query = {
            "text_id": child_text_id,
            "mapping": {
                "$elemMatch": {
                    "text_id": parent_text_id,
                    "segments": {"$in": [parent_segment_id]}
                }
            }
        }
        return await cls.find(query).to_list()