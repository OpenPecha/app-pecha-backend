from typing import Optional, List

from pydantic import BaseModel
from uuid import UUID
from pecha_api.users.users_enums import SocialProfile


class SocialMediaProfile(BaseModel):
    account: SocialProfile
    url: str

class AuthorInfoResponse(BaseModel):
    id: UUID
    firstname: str
    lastname: str
    email: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    social_profiles: List[SocialMediaProfile]

class AuthorsResponse(BaseModel):
    authors: List[AuthorInfoResponse]
    skip: int
    limit: int
    total: int