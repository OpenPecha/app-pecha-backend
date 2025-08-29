from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, Boolean, UUID
from ..db.database import Base
from _datetime import datetime
from uuid import uuid4
import _datetime
from sqlalchemy.orm import relationship

class Author(Base):
    __tablename__ = "authors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    auth0_id = Column(String(255), unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    firstname = Column(String(255), nullable=False)
    lastname = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    registration_source = Column(String(25), nullable=False)
    title = Column(String(255),nullable=True)
    organization = Column(String(255),nullable=True)
    location = Column(String(255),nullable=True)
    education = Column(String(255),nullable=True)
    about_me = Column(String,nullable=True)
    avatar_url = Column(String(255),nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, server_default="FALSE", default=False,nullable=False)
    created_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(_datetime.timezone.utc))

    # Define the relationship between users and social media accounts
    social_media_accounts = relationship("SocialMediaAccount", back_populates="author", cascade="all, delete-orphan")



class CreateAuthorRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class AuthorDetails(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    created_at: datetime
    updated_at: datetime

class AuthorResponse(BaseModel):
    author: AuthorDetails

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class AuthorInfo(BaseModel):
    name: str
    avatar_url: Optional[str] = None

class AuthorLoginRequest(BaseModel):
    email: str
    password: str

class AuthorLoginResponse(BaseModel):
    author: AuthorDetails
    auth: TokenResponse