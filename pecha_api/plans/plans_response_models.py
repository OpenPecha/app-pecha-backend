from pydantic import BaseModel
from typing import Optional, List
from pecha_api.plans.plans_enums import DifficultyLevel, PlanStatus,ContentType
from uuid import UUID

from plans.plans_models import Plan


# Request/Response Models
class CreatePlanRequest(BaseModel):
    title: str
    description: str
    difficulty_level: DifficultyLevel
    total_days: int
    language: str
    image_url: Optional[str] = None
    tags: Optional[List[str]] = []

class UpdatePlanRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    total_days: Optional[int] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None

class PlanStatusUpdate(BaseModel):
    status: PlanStatus

class PlanDTO(BaseModel):
    id: UUID
    title: str
    description: str
    image_url: Optional[str] = None
    total_days: int
    status: PlanStatus
    subscription_count: int

class TaskDTO(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    content_type: ContentType
    content: Optional[str] = None
    estimated_time: Optional[int] = None

class PlanDayDTO(BaseModel):
    id: UUID
    day_number: int
    title: str
    tasks: List[TaskDTO]

class PlanWithDays(BaseModel):
    id: UUID
    title: str
    description: str
    days: List[PlanDayDTO]

class PlansResponse(BaseModel):
    plans: List[PlanDTO]
    skip: int
    limit: int
    total: int



class PlanWithAggregates(BaseModel):
    plan: Plan
    total_days: int
    subscription_count: int

class PlansRepositoryResponse(BaseModel):
    plan_info: List[PlanWithAggregates]
    total: int
