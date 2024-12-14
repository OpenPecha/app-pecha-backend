from sqlalchemy.orm import Session
from .users_models import Users


def save_user(db: Session, user: Users):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first()
