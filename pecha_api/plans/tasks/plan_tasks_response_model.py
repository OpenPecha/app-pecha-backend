from pydantic import BaseModel
from typing import Optional
from pecha_api.plans.plans_enums import ContentType
from uuid import UUID

# Request/Response Models
class CreateTaskRequest(BaseModel):
    plan_id: UUID
    day_id: UUID
    title: str
    description: Optional[str] = None
    estimated_time: Optional[int] = None

class TaskDTO(BaseModel):
    id: UUID
    title: str
    display_order: int
    estimated_time: Optional[int] = None

class UpdatedTaskDayResponse(BaseModel):
    task_id: UUID
    title: str
    day_id: UUID
    display_order: int
    estimated_time: Optional[int] = None

class UpdateTaskDayRequest(BaseModel):
    target_day_id: UUID
