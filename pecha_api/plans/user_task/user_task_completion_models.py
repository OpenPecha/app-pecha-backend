from sqlalchemy import Column, DateTime, Index, UniqueConstraint, UUID, ForeignKey
from uuid import uuid4
from _datetime import datetime
import _datetime
from sqlalchemy.orm import relationship

from ...db.database import Base


class UserTaskCompletion(Base):
    __tablename__ = "user_task_completion"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey('plan_tasks.id', ondelete='CASCADE'), nullable=False)

    completed_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(_datetime.timezone.utc))
    created_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc),nullable=False)

    user = relationship("Users", backref="completed_tasks")
    task = relationship("PlanTask", backref="completions")

    __table_args__ = (
        UniqueConstraint("user_id", "task_id", name="uq_user_task_completion"),
        Index("idx_user_completion_user_task", "user_id", "task_id"),
        Index("idx_user_completion_completed_at", "completed_at"),
    )


