from pydantic import BaseModel
from uuid import UUID

class CreateRecitationsRequest(BaseModel):
    title: str
    audio_url: str
    text_id: UUID
    content: dict
