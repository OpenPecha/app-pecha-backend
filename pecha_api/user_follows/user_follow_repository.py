from ..db import database
from .user_follows_model import UserFollow

def create_user_follow(follower_id: str, following_id: str) -> UserFollow:
    with database.SessionLocal() as db_session:
        new_follow = UserFollow(follower_id=follower_id, following_id=following_id)
        db_session.add(new_follow)
        db_session.commit()
        db_session.refresh(new_follow)
        return new_follow

def get_user_follow_count(following_id: str) -> int:
    with database.SessionLocal() as db_session:
        return db_session.query(UserFollow).filter(UserFollow.following_id == following_id).count()

def is_user_following_target_user(follower_id: str, following_id: str) -> bool:
    with database.SessionLocal() as db_session:
        return db_session.query(UserFollow).filter(UserFollow.follower_id == follower_id, UserFollow.following_id == following_id).first()