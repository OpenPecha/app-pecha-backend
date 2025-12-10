from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index, UniqueConstraint, UUID, String, Boolean, Text
from sqlalchemy.orm import relationship
from uuid import uuid4
from ..db.database import Base
from _datetime import datetime
import _datetime
from sqlalchemy.dialects.postgresql import JSONB

class Thread(Base):
    __tablename__ = "threads"

    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String(255), nullable=False)
    is_deleted = Column(Boolean, default=False) 
    created_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc),nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc))


class Chats(Base):
    __tablename__ = "chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey('threads.id', ondelete='CASCADE'), nullable=False)
    email = Column(String(255), nullable=False)
    question = Column(Text, nullable=False)
    response = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc),nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc))

    thread = relationship("Thread", backref="chats")