from pydantic import BaseModel
from typing import Optional
from pecha_api.plans.plans_enums import ContentType
from uuid import UUID

# Request/Response Models
class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: ContentType
    content: str
    estimated_time: Optional[int] = None

class TaskDTO(BaseModel):
    id: UUID
    title: str
    content_type: ContentType
    content: str
    display_order: int
    estimated_time: Optional[int] = None


