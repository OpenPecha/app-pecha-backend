from sqlalchemy import Column, Integer, DateTime, BigInteger, ForeignKey, Index, UniqueConstraint, UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from ...db.database import Base
from _datetime import datetime
import _datetime


class PlanItem(Base):
    __tablename__ = "plan_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('plans.id', ondelete='CASCADE'), nullable=False)
    day_number = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))

    plan = relationship("Plan", backref="plan_items")

    __table_args__ = (
        UniqueConstraint("plan_id", "day_number", name="uq_plan_items_plan_day"),
        Index("idx_plan_items_plan_day", "plan_id", "day_number"),
    )


