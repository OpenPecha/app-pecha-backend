from sqlalchemy import Column, Integer, DateTime, Boolean, Text, ForeignKey, Index, UUID, String
from sqlalchemy.orm import relationship
from uuid import uuid4
from ...db.database import Base
from ..plans_enums import ContentTypeEnum
from _datetime import datetime
import _datetime


class PlanSubTask(Base):
    __tablename__ = "sub_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)

    content_type = Column(ContentTypeEnum, nullable=False)
    content = Column(Text, nullable=True)

    display_order = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc), nullable=False)
    created_by = Column(String(255), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc))
    updated_by = Column(String(255))

    deleted_at = Column(DateTime(timezone=True))
    deleted_by = Column(String(255))

    # Relationships
    task = relationship("PlanTask", backref="sub_tasks")

    __table_args__ = (
        Index("idx_sub_tasks_task_order", "task_id", "display_order"),
        Index("idx_sub_tasks_content_type", "content_type"),
    )