from typing import Optional

from pydantic import BaseModel


class CreateAuthorRequest(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str