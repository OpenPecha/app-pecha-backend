from sqlalchemy import Column, String, DateTime, Boolean, UUID, Text, Index, text
from sqlalchemy.orm import relationship

from pecha_api.db.database import Base
from uuid import uuid4
import _datetime
from _datetime import datetime

class Author(Base):
    __tablename__ = "authors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name = Column(String(200), nullable=False)
    last_name = Column(String(200), nullable=False)
    bio = Column(Text, nullable=True)
    image_url = Column(String(1000), nullable=True)
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


    __table_args__ = (
        Index("idx_authors_verified", "is_verified", postgresql_where=text("is_verified = TRUE")),
    )
