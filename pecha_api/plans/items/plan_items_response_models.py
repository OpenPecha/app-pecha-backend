from pydantic import BaseModel
from uuid import UUID


class ItemDBInput(BaseModel):
    plan_id: UUID
    day_number: int

class ItemDTO(BaseModel):
    id: UUID
    plan_id: UUID
    day_number: int

class UpdateDayRequest(BaseModel):
    day_number: int