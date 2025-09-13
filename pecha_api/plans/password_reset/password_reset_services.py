from pecha_api.db import SessionLocal
from pecha_api.auth.auth_service import get_user_by_email
from pecha_api.auth.auth_models import PasswordReset
from pecha_api.auth.auth_repository import save_password_reset
from pecha_api.config import get
from pecha_api.notification.email_provider import send_email
from fastapi import HTTPException
from starlette import status
import secrets
from datetime import datetime, timedelta, timezone


def request_reset_password(email: str):
    with SessionLocal() as db_session:
        current_user = get_user_by_email(
            db=db_session,
            email=email
        )
        if current_user.registration_source != 'email':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration Source Mismatch")

        reset_token = secrets.token_urlsafe(32)
        token_expiry = datetime.now(timezone.utc) + timedelta(minutes=30)
        password_reset = PasswordReset(
            email=current_user.email,
            reset_token=reset_token,
            token_expiry=token_expiry
        )
        save_password_reset(
            db=db_session,
            password_reset=password_reset
        )
        reset_link = f"{get('BASE_URL')}/reset-password?token={reset_token}"
        send_reset_email(email=email, reset_link=reset_link)
        return {"message": "If the email exists in our system, a password reset email has been sent."}


def update_password(token: str, password: str):
    with SessionLocal() as db_session:
        reset_entry = get_password_reset_by_token(
            db=db_session,
            token=token
        )
        if reset_entry is None or reset_entry.token_expiry < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
        current_user = get_user_by_email(
            db=db_session,
            email=reset_entry.email
        )
        if current_user.registration_source != 'email':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration Source Mismatch")

        _validate_password(password)
        hashed_password = get_hashed_password(password)
        current_user.password = hashed_password
        updated_user = save_user(db=db_session, user=current_user)
        return updated_user