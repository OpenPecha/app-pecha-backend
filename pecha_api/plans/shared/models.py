from typing import List
from pydantic import BaseModel


class SubTaskModel(BaseModel):
    id: str
    content_type: str
    content: str
    display_order: int

class TaskModel(BaseModel):
    id: str
    title: str
    description: str
    estimated_time: int
    subtasks: List[SubTaskModel]



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
    language: str
    status: str
    subscription_count: int
    days: List[DayModel]


class PlanListingModel(BaseModel):
    plans: List[PlanModel]
    skip: int
    limit: int
    total: int
