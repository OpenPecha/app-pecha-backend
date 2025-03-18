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