from typing import Optional

from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str