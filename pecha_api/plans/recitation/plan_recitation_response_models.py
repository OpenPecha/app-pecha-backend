from pydantic import BaseModel
from uuid import UUID

class CreateRecitationRequest(BaseModel):
    title: str
    audio_url: str
    content: dict
