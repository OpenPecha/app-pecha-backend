from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

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


class AuthorLoginResponse(BaseModel):
    user: AuthorInfo
    auth: TokenResponse

class AuthorLoginRequest(BaseModel):
    email: str
    password: str