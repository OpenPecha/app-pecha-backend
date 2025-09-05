from pydantic import BaseModel
from datetime import datetime

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

<<<<<<< HEAD:pecha_api/plans/plan_auth/plan_auth_model.py
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class AuthorInfo(BaseModel):
    name: str
    avatar_url: Optional[str] = None


class AuthorLoginResponse(BaseModel):
    user: AuthorInfo
    auth: TokenResponse

class AuthorLoginRequest(BaseModel):
    email: str
    password: str
=======
class TokenPayload(BaseModel):
    email: str
    iss: str
    aud: str
    iat: datetime
    exp: datetime
    typ: str
>>>>>>> 4c74737b4589a67d39512f69e1c9c494c36fc08e:pecha_api/plans/auth/plan_auth_model.py
