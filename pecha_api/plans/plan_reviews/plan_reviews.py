from sqlalchemy import Column, Integer, DateTime, Boolean, Text, ForeignKey, Index, UniqueConstraint, UUID, CheckConstraint, text
from sqlalchemy.orm import relationship
from uuid import uuid4
from ...db.database import Base
from _datetime import datetime
import _datetime


class PlanReview(Base):
    __tablename__ = "plan_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('plans.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)

    is_approved = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))

    plan = relationship("Plan", backref="reviews")
    user = relationship("Users", backref="plan_reviews")

    __table_args__ = (
        UniqueConstraint("user_id", "plan_id", name="uq_plan_reviews_user_plan"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="chk_plan_reviews_rating"),
        Index("idx_plan_reviews_plan_approved", "plan_id", "is_approved", postgresql_where=text("is_approved = TRUE")),
        Index("idx_plan_reviews_rating", "plan_id", "rating"),
    )


