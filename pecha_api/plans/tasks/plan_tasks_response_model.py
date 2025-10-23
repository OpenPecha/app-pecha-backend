from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from typing import List
from pecha_api.plans.tasks.sub_tasks.plan_sub_tasks_response_model import SubTaskDTO

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
    title: Optional[str] = None

class GetTaskRequest(BaseModel):
    task_id: UUID

class GetTaskResponse(BaseModel):
    id: UUID
    title: str
    display_order: int
    estimated_time: Optional[int] = None
    subtasks: List[SubTaskDTO]