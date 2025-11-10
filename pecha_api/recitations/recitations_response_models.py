from typing import List
from pydantic import BaseModel
from uuid import UUID

class TextSegments(BaseModel):
    text: str
    segment_id: str
    start_time: str
    end_time: str

class RecitationContent(BaseModel):
    content: List[TextSegments]

class CreateRecitationsRequest(BaseModel):
    title: str
    audio_url: str
    text_id: UUID
    content: RecitationContent
