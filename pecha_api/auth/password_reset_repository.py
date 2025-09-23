from sqlalchemy.orm import Session
from ..users.users_models import PasswordReset
from ..plans.authors.plan_author_model import AuthorPasswordReset


def save_password_reset(db: Session, password_reset: PasswordReset):
    db.add(password_reset)
    db.commit()
    db.refresh(password_reset)
    return password_reset


def get_password_reset_by_token(db: Session, token: str):
    return db.query(PasswordReset).filter(PasswordReset.reset_token == token).first()


def get_password_reset_by_token_for_author(db: Session, token: str):
    return db.query(AuthorPasswordReset).filter(AuthorPasswordReset.reset_token == token).first()
