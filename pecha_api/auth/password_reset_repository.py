from sqlalchemy.orm import Session

from users.users_models import PasswordReset


def save_password_reset(db: Session, password_reset: PasswordReset):
    db.add(password_reset)
    db.commit()
    db.refresh(password_reset)
    return password_reset
