from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from .user_follow_response_models import FollowUserRequest
from .user_follow_services import post_user_follow


oauth2_scheme = HTTPBearer()
user_follow_router = APIRouter(
    prefix="/users",
    tags=["User Follows"]
)


@user_follow_router.post("/follow", status_code=status.HTTP_204_NO_CONTENT)
def follow_user(follow_request: FollowUserRequest, authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]
):
    post_user_follow(token=authentication_credential.credentials, following_username=follow_request.username)



