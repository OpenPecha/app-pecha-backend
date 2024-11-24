from sqlalchemy import Column, Integer, String, DateTime, Boolean
from ..db.database import Base
from _datetime import datetime
import _datetime


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String,nullable=False)
    lastname = Column(String, nullable=False)
    admin = Column(Boolean, default=False)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))
    