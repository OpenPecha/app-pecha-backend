from sqlalchemy import Column, Integer, String, DateTime, Boolean, UUID, ForeignKey
from ..db.database import Base
from _datetime import datetime
from uuid import uuid4
import _datetime
from sqlalchemy.orm import relationship


class Author(Base):
    __tablename__ = "authors"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    bio = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))

    __table_args__ = (
        Index("idx_authors_verified", "is_verified", postgresql_where=text("is_verified = TRUE")),
    )