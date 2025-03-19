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
        return await cls.find_one(cls.id == segment_id)
    
    @classmethod
    async def get_segment_by_list_of_id(cls, segment_ids: List[str]):
        return await cls.find({"_id": {"$in": segment_ids}}).to_list(length=len(segment_ids))