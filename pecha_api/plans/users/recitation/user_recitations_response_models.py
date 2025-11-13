from pydantic import BaseModel
from uuid import UUID
from typing import List

class CreateUserRecitationRequest(BaseModel):
    text_id: UUID

class UserRecitationDTO(BaseModel):
    title: str
    text_id: UUID

class UserRecitationsResponse(BaseModel):
    recitations: List[UserRecitationDTO]