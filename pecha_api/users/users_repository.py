from sqlalchemy.orm import Session
from .users_models import Users
from fastapi import HTTPException
from starlette import status


def save_user(db: Session, user: Users):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    user = db.query(Users).filter(Users.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
