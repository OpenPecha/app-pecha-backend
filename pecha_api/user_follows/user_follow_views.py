from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from .user_follow_response_models import FollowUserRequest, FollowUserResponse
from .user_follow_services import post_user_follow


oauth2_scheme = HTTPBearer()
user_follow_router = APIRouter(
    prefix="/users",
    tags=["User Follows"]
)


@user_follow_router.post("/follow", status_code=status.HTTP_201_CREATED, response_model=FollowUserResponse)
def follow_user(follow_request: FollowUserRequest, authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]
) -> FollowUserResponse:
    user_follow_response: FollowUserResponse = post_user_follow(token=authentication_credential.credentials, following_username=follow_request.username)
    return user_follow_response



