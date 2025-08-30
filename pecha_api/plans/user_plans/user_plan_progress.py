from sqlalchemy import Column, DateTime, Boolean, Integer, Index, UniqueConstraint, UUID, ForeignKey
from sqlalchemy import Enum as SQLEnum
from uuid import uuid4
from _datetime import datetime
import _datetime
from sqlalchemy.orm import relationship

from ...db.database import Base
from ...plans.plan_enums import UserPlanStatus


class UserPlanProgress(Base):
    __tablename__ = "user_plan_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('plans.id', ondelete='CASCADE'), nullable=False)

    started_at = Column(DateTime, nullable=False, default=datetime.now(_datetime.timezone.utc))

    streak_count = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)

    status = Column(SQLEnum(UserPlanStatus, name="user_plan_status", native_enum=True), default=UserPlanStatus.active)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))

    user = relationship("Users", backref="plan_progress")
    plan = relationship("Plan", backref="user_progress")

    __table_args__ = (
        UniqueConstraint("user_id", "plan_id", name="uq_user_plan_progress_user_plan"),
        Index("idx_user_progress_user_status", "user_id", "status"),
        Index("idx_user_progress_plan", "plan_id"),
    )


