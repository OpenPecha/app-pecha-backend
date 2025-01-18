from sqlite3 import IntegrityError

from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session
from .users_models import Users, SocialMediaAccount
from fastapi import HTTPException
from starlette import status


def save_user(db: Session, user: Users):
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


def update_user(db: Session, user: Users) -> Users:
    try:
        updated_user = db.merge(user)
        db.commit()
        db.refresh(updated_user)
        return updated_user
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User update issue")
    except InvalidRequestError as e:
        db.rollback()
        print(f"InvalidRequestError error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid update request")


def get_user_by_email(db: Session, email: str):
    user = db.query(Users).filter(Users.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def get_user_by_username(db: Session, username: str):
    user = db.query(Users).filter(Users.username == username).first()
    return user


def get_user_social_account(db: Session, user_id: str):
    social_accounts = db.query(SocialMediaAccount).filter(SocialMediaAccount.user_id == user_id)
    return social_accounts
