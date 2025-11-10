from typing import List
from pydantic import BaseModel
from uuid import UUID
class Content(BaseModel):
    text: str
    segment_id: str
    start_time: float
    end_time: float

class CreateRecitationsRequest(BaseModel):
    title: str
    audio_url: str
    text_id: UUID
    content: dict
