from pydantic import BaseModel

class PasswordResetRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    password: str