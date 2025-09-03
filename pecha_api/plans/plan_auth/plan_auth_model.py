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

class TokenPayload(BaseModel):
    email: str
    iss: str
    aud: str
    iat: datetime
    exp: datetime
    typ: str