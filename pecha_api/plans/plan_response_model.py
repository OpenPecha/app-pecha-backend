from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class PlanRequest(BaseModel):
    difficulty_level: Optional[str] = None
    tags: Optional[list[str]] = None
    featured: Optional[bool] = None
    skip: int = 0
    limit: int = 10

class PlanAuthorDetails(BaseModel):
    id: UUID
    email: str
    image_url: str

class PlanListDetails(BaseModel):
    id: UUID
    title: str
    description: str
    author_id: PlanAuthorDetails
    language: str
    difficulty_level: str
    tags: list[str]
    featured: bool
    is_active: bool
    image_url: str
    plan_days: int
    plan_used_count: int



class PlanResponse(BaseModel):
    plan: list[PlanListDetails]
    total: int
    skip: int
    limit: int
