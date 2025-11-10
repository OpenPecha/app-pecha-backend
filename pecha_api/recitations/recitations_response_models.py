from typing import List
from pydantic import BaseModel
from uuid import UUID

class TextSegments(BaseModel):
    text: str
    segment_id: UUID
    start_time: str
    end_time: str

class RecitationContent(BaseModel):
    texts: List[TextSegments]

class CreateRecitationsRequest(BaseModel):
    title: str
    audio_url: str
    text_id: UUID
    content: RecitationContent
