from typing import Optional

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..users.models import Users

SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def save_user(db: Session, user: Users):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first()


def get_hashed_password(password):
    return pwd_context.hash(password)


