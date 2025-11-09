from pydantic import BaseModel
from uuid import UUID
from typing import List


class ItemDBInput(BaseModel):
    plan_id: UUID
    day_number: int

class ItemDTO(BaseModel):
    id: UUID
    plan_id: UUID
    day_number: int

class UpdateDayRequest(BaseModel):
    day_number: int

class ItemDayNumberDTO(BaseModel):
    id: UUID
    day_number: int

class ReorderDaysRequest(BaseModel):
    days: List[ItemDayNumberDTO]