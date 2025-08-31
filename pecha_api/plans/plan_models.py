from sqlalchemy import Column, String, DateTime, Boolean, UUID, Text, Index, text, ForeignKey
from ..db.database import Base
from uuid import uuid4
import _datetime
from _datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .plan_enums import LanguageCodeEnum, DifficultyLevelEnum, PlanStatusEnum, DifficultyLevel, PlanStatus, LanguageCode
from sqlalchemy import Enum as SQLEnum

class Author(Base):
    __tablename__ = "authors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name = Column(String(200), nullable=False)
    last_name = Column(String(200), nullable=False)
    bio = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc),nullable=False)
    created_by = Column(String(255), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc))
    updated_by = Column(String(255))
    deleted_at = Column(DateTime(timezone=True))
    deleted_by = Column(String(255))

    plans = relationship("Plan", back_populates="author")

    __table_args__ = (
        Index("idx_authors_verified", "is_verified", postgresql_where=text("is_verified = TRUE")),
    )


class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey('authors.id', ondelete='RESTRICT'), nullable=False)
    language = Column(LanguageCodeEnum, nullable=False, default='en')
    difficulty_level = Column(DifficultyLevelEnum, default='BEGINNER')

    tags = Column(JSONB, server_default=text("'[]'::jsonb"), nullable=False)
    featured = Column(Boolean, default=False,nullable=False)
    status = Column(PlanStatusEnum, nullable=False, default='DRAFT')
    # Content metadata
    image_url = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc),nullable=False)
    created_by = Column(String(255), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc))
    updated_by = Column(String(255))

    deleted_at = Column(DateTime(timezone=True))
    deleted_by = Column(String(255))


    author = relationship("Author", backref="plans", passive_deletes=True)
    plan_items = relationship("PlanItem", back_populates="plan", cascade="all, delete-orphan")
    user_progress = relationship("UserPlanProgress", back_populates="plan", cascade="all, delete-orphan")
    reviews = relationship("PlanReview", back_populates="plan", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="plan", cascade="all, delete-orphan")

    __table_args__ = (
        # Indexes for plan discovery
        Index("idx_plans_discovery", "tags", "status"),
        Index("idx_plans_featured", "featured", postgresql_where=text("featured = TRUE")),
        Index("idx_plans_search", text("to_tsvector('english', title || ' ' || COALESCE(description, ''))"),
              postgresql_using="gin"),
        Index("idx_plans_tags", "tags", postgresql_using="gin"),
    )

