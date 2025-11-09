from typing import List
from pydantic import BaseModel
from uuid import UUID

class CreateRecitationRequest(BaseModel):
    title: str
    audio_url: str
    text_id: UUID
    content: dict

class RecitationDTO(BaseModel):
    id: UUID
    title: str
    audio_url: str
    text_id: UUID
    content: dict

class RecitationsResponse(BaseModel):
    recitations: List[RecitationDTO]
    skip: int
    limit: int
    total: int