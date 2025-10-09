from fastapi import HTTPException
from starlette import status
from ..db import database
from ..users.users_repository import get_user_by_username   
from ..users.users_service import validate_and_extract_user_details
from .user_follow_repository import create_user_follow, is_user_following_target_user
from ..error_contants import ErrorConstants

def post_user_follow(token: str, following_username: str) -> None:
    current_user = validate_and_extract_user_details(token=token)
    with database.SessionLocal() as db_session:
        target_user = get_user_by_username(db=db_session, username=following_username)

        if target_user.id == current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.BAD_REQUEST_FOLLOW_YOURSELF)

        existing_follow = is_user_following_target_user(follower_id=current_user.id, following_id=target_user.id)

        if existing_follow is None:
            create_user_follow(follower_id=current_user.id, following_id=target_user.id)