from pydantic import BaseModel


class UserInfoResponse(BaseModel):
    firstname: str
    lastname: str
    email: str
    followers: int
    following: int
    avatar_url: str