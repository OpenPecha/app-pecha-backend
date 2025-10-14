from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from pecha_api.plans.plans_enums import DifficultyLevel, PlanStatus,ContentType
from uuid import UUID
from pecha_api.plans.plans_models import Plan


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

class AuthorDTO(BaseModel):
    id: UUID
    firstname: str
    lastname: str
    image_url: str

class PlanDTO(BaseModel):
    id: UUID
    title: str
    description: str
    language: str
    image_url: Optional[str] = None
    total_days: int
    status: PlanStatus
    subscription_count: int
    author: Optional[AuthorDTO] = None

class SubTaskDTO(BaseModel):
    """Subtask model for tasks without titles but with different content types"""
    id: UUID
    content_type: ContentType
    content: Optional[str] = None
    display_order: Optional[int] = None

class TaskDTO(BaseModel):
    id: UUID
    title: Optional[str] = None  # Made optional to support subtasks
    estimated_time: Optional[int] = None
    display_order: Optional[int] = None
    subtasks: List[SubTaskDTO] = []

class PlanDayDTO(BaseModel):
    id: UUID
    day_number: int
    tasks: List[TaskDTO]

class PlanWithDays(BaseModel):
    id: UUID
    title: str
    description: str
    language: str
    image_url: Optional[str] = None
    total_days: int
    difficulty_level: str
    tags: List[str]
    days: List[PlanDayDTO]

class PlansResponse(BaseModel):
    plans: List[PlanDTO]
    skip: int
    limit: int
    total: int

class PlanWithAggregates(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    plan: Plan
    total_days: int
    subscription_count: int

class PlansRepositoryResponse(BaseModel):
    plan_info: List[PlanWithAggregates]
    total: int

# Update forward references for nested models
TaskDTO.model_rebuild()
