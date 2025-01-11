from pydantic import BaseModel

from users.users_enums import SocialProfile


class SocialMediaProfile(BaseModel):
    account: SocialProfile
    url: str

class UserInfoRequest(BaseModel):
    firstname: str
    lastname: str
    title: str
    organization: str
    educations: [str]
    avatar_url: str
    about_me: str
    social_profiles: [SocialMediaProfile]

class UserInfoResponse(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: str
    title: str
    organization: str
    educations: [str]
    avatar_url: str
    about_me: str
    followers: int
    following: int
    social_profiles: [SocialMediaProfile]
