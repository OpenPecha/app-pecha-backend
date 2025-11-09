from pydantic import BaseModel
from uuid import UUID

class CreateUserRecitationRequest(BaseModel):
    recitation_id: UUID