from pydantic import BaseModel
from pecha_api.plans.plans_enums import ContentType
from typing import List
from uuid import UUID



class SubTaskRequestFields(BaseModel):
    content_type: str
    content: str


class SubTaskRequest(BaseModel):
    task_id: UUID
    sub_tasks: List[SubTaskRequestFields]


class SubTaskDTO(BaseModel):
    id: UUID
    content_type: ContentType
    content: str
    display_order: int

class SubTaskResponse(BaseModel):
    sub_tasks: List[SubTaskDTO]
