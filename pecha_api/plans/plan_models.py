from sqlalchemy import Column, String, DateTime, Boolean, UUID, Text, Index, text
from ..db.database import Base
from uuid import uuid4
import _datetime
from _datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB


class Author(Base):
    __tablename__ = "authors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name = Column(String(200), nullable=False)
    last_name = Column(String(200), nullable=False)
    bio = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))

    __table_args__ = (
        Index("idx_authors_verified", "is_verified", postgresql_where=text("is_verified = TRUE")),
    )


class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    author_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to authors table
    language = Column(String(10), default='en')
    
    tags = Column(JSONB, nullable=True)
    featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Content metadata
    image_url = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))

    __table_args__ = (
        # Indexes for plan discovery
        Index("idx_plans_discovery", "tags", "is_active"),
        Index("idx_plans_featured", "featured", postgresql_where=text("featured = TRUE")),
        Index("idx_plans_search", text("to_tsvector('english', title || ' ' || COALESCE(description, ''))"), postgresql_using="gin"),
        Index("idx_plans_tags", "tags", postgresql_using="gin"),
    )

