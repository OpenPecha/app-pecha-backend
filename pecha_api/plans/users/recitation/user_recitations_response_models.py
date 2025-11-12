from pydantic import BaseModel
from uuid import UUID

class CreateUserRecitationRequest(BaseModel):
    text_id: UUID