from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class UserPlanEnrollRequest(BaseModel):
    plan_id: UUID


class UserPlanStatus(BaseModel):
    status: str  # not_started, active, paused, completed, abandoned


class UserPlanProgress(BaseModel):
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


class UserPlanProgressUpdate(BaseModel):
    status: str
