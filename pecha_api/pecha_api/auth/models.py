
from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: str
    password: str