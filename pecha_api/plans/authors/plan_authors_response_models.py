from typing import Optional, List

from pydantic import BaseModel
from uuid import UUID
from pecha_api.users.users_enums import SocialProfile


class SocialMediaProfile(BaseModel):
    account: SocialProfile
    url: str

class AuthorUpdateResponse(BaseModel):
    id: UUID
    firstname: str
    lastname: str
    email: str
    image_url: str
    image_key: str
    bio: Optional[str] = None


class AuthorInfoRequest(BaseModel):
    firstname: str
    lastname: str
    image_url: Optional[str] = None
    bio: Optional[str] = None
    social_profiles: List[SocialMediaProfile]

class AuthorInfoResponse(BaseModel):
    id: UUID
    firstname: str
    lastname: str
    email: str
    image_url: Optional[str] = None
    bio: Optional[str] = None
    social_profiles: List[SocialMediaProfile]

class AuthorsResponse(BaseModel):
    authors: List[AuthorInfoResponse]
    skip: int
    limit: int
    total: int