from pydantic import BaseModel


class FollowUserRequest(BaseModel):
    username: str

