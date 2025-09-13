from typing import List
from pydantic import BaseModel


class PlanDayBasic(BaseModel):
    id: str
    day_number: int
    title: str


class PlanDaysResponse(BaseModel):
    days: List[PlanDayBasic]
