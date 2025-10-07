from pydantic import BaseModel


class FollowUserRequest(BaseModel):
    username: str


class FollowUserResponse(BaseModel):
    message: str
    is_following: bool
    follower_count: int