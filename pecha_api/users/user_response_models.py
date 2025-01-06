from pydantic import BaseModel

from users.users_enums import SocialProfile


class SocialMediaProfile(BaseModel):
    account: SocialProfile
    url: str


class UserInfoResponse(BaseModel):
    firstname: str
    lastname: str
    email: str
    title: str
    organization: str
    educations: [str]
    avatar_url: str
    followers: int
    following: int
    social_profiles: [SocialMediaProfile]
