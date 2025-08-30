from sqlalchemy import Column, Integer, DateTime, Boolean, Text, ForeignKey, Index, UUID
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from uuid import uuid4
from ...db.database import Base
from ..plan_enums import ContentType
from _datetime import datetime
import _datetime


class PlanTask(Base):
    __tablename__ = "plan_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    plan_item_id = Column(UUID(as_uuid=True), ForeignKey('plan_items.id', ondelete='CASCADE'), nullable=False)

    title = Column(Text, nullable=True)
    content_type = Column(SQLEnum(ContentType, name="content_type", native_enum=True), nullable=False)
    content = Column(Text, nullable=True)

    display_order = Column(Integer, nullable=False)
    estimated_time = Column(Integer, nullable=True)  # minutes
    is_required = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))

    plan_item = relationship("PlanItem", backref="tasks")

    __table_args__ = (
        Index("idx_tasks_plan_item_order", "plan_item_id", "display_order"),
        Index("idx_tasks_content_type", "content_type"),
    )


