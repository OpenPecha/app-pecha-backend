from typing import List, Optional
from uuid import UUID
from pecha_api.plans.plans_enums import ContentType
from pydantic import BaseModel


class PlanDayBasic(BaseModel):
    id: str
    day_number: int


class PlanDaysResponse(BaseModel):
    days: List[PlanDayBasic]

class SubTaskDTO(BaseModel):
    """Subtask model for tasks without titles but with different content types"""
    id: UUID
    content_type: ContentType
    content: Optional[str] = None
    display_order: Optional[int] = None

class TaskDTO(BaseModel):
    id: UUID
    title: Optional[str] = None
    estimated_time: Optional[int] = None
    display_order: Optional[int] = None
    subtasks: List[SubTaskDTO] = []

class PlanDayDTO(BaseModel):
    id: UUID
    day_number: int
    tasks: List[TaskDTO]