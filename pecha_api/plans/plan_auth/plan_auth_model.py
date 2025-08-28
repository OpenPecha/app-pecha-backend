from typing import Optional

from pydantic import BaseModel


class CreateAuthorRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str