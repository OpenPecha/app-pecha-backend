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
