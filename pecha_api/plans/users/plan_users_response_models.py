from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class UserPlanEnrollRequest(BaseModel):
    plan_id: UUID


class UserPlanStatus(BaseModel):
    status: str  # not_started, active, paused, completed, abandoned


class UserPlanProgressResponse(BaseModel):
    id: UUID
    user_id: UUID
    plan_id: UUID
    plan: dict  # Will contain plan details
    started_at: datetime
    streak_count: int
    longest_streak: int
    status: str
    is_completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime

class EnrolledUserPlan(BaseModel):
    user_id: UUID
    plan_id: UUID
    streak_count: int
    longest_streak: int
    status: str
    created_at: datetime
    is_completed: bool

class UserPlansResponse(BaseModel):
    id: UUID
    title: str
    description: str
    language: str
    difficulty_level: str
    image_url: str
    started_at: datetime
    total_days: int
    tags: List[str]

class UserPlanProgressUpdate(BaseModel):
    status: str
