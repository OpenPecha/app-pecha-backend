from typing import Optional

from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserInfo(BaseModel):
    name: str
    avatar_url: Optional[str] = None


class UserLoginResponse(BaseModel):
    user: UserInfo
    auth: TokenResponse


class RefreshTokenRequest(BaseModel):
    token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str


class PasswordResetRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    password: str
