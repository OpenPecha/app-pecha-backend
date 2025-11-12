from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

class RecitationDTO(BaseModel):
    title: str
    text_id: UUID

class RecitationsResponse(BaseModel):
    recitations: List[RecitationDTO]
