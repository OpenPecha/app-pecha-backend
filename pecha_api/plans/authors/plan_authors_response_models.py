from typing import Optional, List

from pydantic import BaseModel

from pecha_api.users.users_enums import SocialProfile


class SocialMediaProfile(BaseModel):
    account: SocialProfile
    url: str

class AuthorInfoResponse(BaseModel):
    firstname: str
    lastname: str
    email: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    social_profiles: List[SocialMediaProfile]