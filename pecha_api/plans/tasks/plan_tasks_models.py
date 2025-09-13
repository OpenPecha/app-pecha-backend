from sqlalchemy import Column, Integer, DateTime, Boolean, Text, ForeignKey, Index, UUID,String
from sqlalchemy.orm import relationship
from uuid import uuid4
from ...db.database import Base
from ..plans_enums import ContentTypeEnum
from _datetime import datetime
import _datetime


class PlanTask(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    plan_item_id = Column(UUID(as_uuid=True), ForeignKey('items.id', ondelete='CASCADE'), nullable=False)

    title = Column(Text, nullable=True)
    content_type = Column(ContentTypeEnum, nullable=False)
    content = Column(Text, nullable=True)

    display_order = Column(Integer, nullable=False)
    estimated_time = Column(Integer, nullable=True)  # minutes
    is_required = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc),nullable=False)
    created_by = Column(String(255), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc))
    updated_by = Column(String(255))

    deleted_at = Column(DateTime(timezone=True))
    deleted_by = Column(String(255))

    plan_item = relationship("PlanItem", backref="tasks", cascade="all, delete-orphan")
    user_completions = relationship("UserTaskCompletion", backref="task", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_tasks_plan_item_order", "plan_item_id", "display_order"),
        Index("idx_tasks_content_type", "content_type"),
    )


