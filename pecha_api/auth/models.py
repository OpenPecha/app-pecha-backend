
from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str