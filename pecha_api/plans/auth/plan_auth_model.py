from pydantic import BaseModel

from pecha_api.plans.auth.plan_auth_enums import AuthorStatus


class CreateAuthorRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class AuthorDetails(BaseModel):
    first_name: str
    last_name: str
    email: str
    status: AuthorStatus
    message: str


class AuthorResponse(BaseModel):
    author: AuthorDetails
