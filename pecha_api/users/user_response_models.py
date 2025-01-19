from typing import List, Optional

from pydantic import BaseModel
from .users_enums import SocialProfile

class SocialMediaProfile(BaseModel):
    account: SocialProfile
    url: str

class UserInfoRequest(BaseModel):
    firstname: str
    lastname: str
    title: Optional[str] = None
    organization: Optional[str] = None
    location: Optional[str] = None
    educations: List[str]
    avatar_url : Optional[str] = None
    about_me: Optional[str] = None
    social_profiles: List[SocialMediaProfile]

class UserInfoResponse(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: str
    title: Optional[str] = None
    organization: Optional[str] = None
    location: Optional[str] = None
    educations: List[str]
    avatar_url: Optional[str] = None
    about_me: Optional[str] = None
    followers: int
    following: int
    social_profiles: List[SocialMediaProfile]
