from fastapi import HTTPException
from starlette import status
from .user_follow_response_models import FollowUserResponse
from .user_follows_model import UserFollow
from ..db import database
from ..users.users_repository import get_user_by_username   
from ..users.users_service import validate_and_extract_user_details
from .user_follow_repository import post_user_follow, get_user_follow_count,is_user_following_target_user


def post_user_follow(token: str, following_username: str) -> FollowUserResponse:
    current_user = validate_and_extract_user_details(token=token)
    with database.SessionLocal() as db_session:
        target_user = get_user_by_username(db=db_session, username=following_username)
        if target_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if target_user.id == current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request - Cannot follow yourself")

        existing_follow = is_user_following_target_user(follower_id=current_user.id, following_id=target_user.id)

        if existing_follow is None:
            post_user_follow(follower_id=current_user.id, following_id=target_user.id)
        follower_count = get_user_follow_count(following_id=target_user.id)

        return FollowUserResponse(
            message="success",
            is_following=True,
            follower_count=follower_count,
        )