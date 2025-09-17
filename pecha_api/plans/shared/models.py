from typing import List
from pydantic import BaseModel


class TaskModel(BaseModel):
    id: str
    title: str
    description: str
    content_type: str
    content: str
    estimated_time: int


class DayModel(BaseModel):
    id: str
    day_number: int
    title: str
    tasks: List[TaskModel]


class PlanModel(BaseModel):
    id: str
    title: str
    description: str
    image_url: str
    total_days: int
    status: str
    subscription_count: int
    days: List[DayModel]


class PlanListingModel(BaseModel):
    plans: List[PlanModel]
    skip: int
    limit: int
    total: int
