from sqlalchemy import Column, Integer, String, DateTime, Boolean, UUID, ForeignKey
from ..db.database import Base
from _datetime import datetime
from uuid import uuid4
import _datetime


class Users(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    auth0_id = Column(String(255), unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    firstname = Column(String(255), nullable=False)
    lastname = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    registration_source = Column(String(25), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))


class PasswordReset(Base):
    __tablename__ = "password_resets"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, ForeignKey("users.email", ondelete="CASCADE"), nullable=False)
    reset_token = Column(String(255), nullable=False, unique=True, index=True)
    token_expiry = Column(DateTime, nullable=False)
