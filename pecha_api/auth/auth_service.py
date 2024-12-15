import uuid
from datetime import datetime, timedelta, timezone

import jwt
from ..config import get
from ..notification.email_provider import send_email
from .auth_models import CreateUserRequest, UserLoginResponse, RefreshTokenResponse, TokenResponse, UserInfo
from ..users.users_models import Users, PasswordReset
from ..db.database import SessionLocal
from ..users.user_repository import get_user_by_email, save_user
from .auth_repository import get_hashed_password, verify_password, create_access_token, create_refresh_token, \
    generate_token_data, decode_token
from .password_reset_repository import save_password_reset, get_password_reset_by_token
from .auth_enums import RegistrationSource
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette import status
from jinja2 import Template
from pathlib import Path


def register_user_with_source(create_user_request: CreateUserRequest, registration_source: RegistrationSource):
    try:
        registered_user = _create_user(
            create_user_request=create_user_request,
            registration_source=registration_source
        )
        return generate_token_user(registered_user)
    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code,
                            content={"message": exception.detail})


def _create_user(create_user_request: CreateUserRequest, registration_source: RegistrationSource) -> Users:
    db_session = SessionLocal()
    try:
        new_user = Users(**create_user_request.model_dump())
        if registration_source == RegistrationSource.EMAIL:
            _validate_password(new_user.password)
            hashed_password = get_hashed_password(new_user.password)
            new_user.password = hashed_password
        new_user.registration_source = registration_source.value
        saved_user = save_user(db=db_session, user=new_user)
        return saved_user
    finally:
        db_session.close()


def _validate_password(password: str):
    if not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password cannot be empty")
    if len(password) < 8 or len(password) > 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Password must be between 8 and 20 characters")


def validate_user_already_exist(email: str):
    db_session = SessionLocal()
    try:
        existing_user_by_email = get_user_by_email(db=db_session, email=email)
        if existing_user_by_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email or username already exists')
    finally:
        db_session.close()


def authenticate_and_generate_tokens(email: str, password: str):
    try:
        user = authenticate_user(email=email, password=password)
        return generate_token_user(user)
    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code,
                            content={"message": exception.detail})


def generate_token_user(user: Users):
    try:
        data = generate_token_data(user)
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)

        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer"
        )
        return UserLoginResponse(
            user=UserInfo(
                name=user.firstname + " " + user.lastname,
                avatar_url=_get_user_avatar(user=user)
            ),
            auth=token_response
        )
    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code,
                            content={"message": exception.detail})


def authenticate_user(email: str, password: str):
    db_session = SessionLocal()
    try:
        user = get_user_by_email(db=db_session, email=email)
        if not verify_password(
                plain_password=password,
                hashed_password=user.password
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')
        return user
    finally:
        db_session.close()


def refresh_access_token(refresh_token: str):
    try:
        db_session = SessionLocal()
        payload = decode_token(refresh_token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        user = get_user_by_email(
            db=db_session,
            email=email
        )
        data = generate_token_data(user)
        access_token = create_access_token(data=data)
        return RefreshTokenResponse(
            access_token=access_token,
            token_type="Bearer"
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


def request_reset_password(email: str):
    db_session = SessionLocal()
    current_user = get_user_by_email(
        db=db_session,
        email=email
    )
    reset_token = str(uuid.uuid4())
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
    reset_link = f"{get("BASE_URL")}/reset-password?token={reset_token}"
    send_reset_email(email=email, reset_link=reset_link)
    return {"message": "If the email exists in our system, a password reset email has been sent."}


def update_password(token: str, password: str):
    db_session = SessionLocal()
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
    _validate_password(password)
    hashed_password = get_hashed_password(password)
    current_user.password = hashed_password
    updated_user = save_user(db=db_session, user=current_user)
    return updated_user


def send_reset_email(email: str, reset_link: str):
    template_path = Path(__file__).parent / "templates" / "reset_password_template.html"
    with open(template_path, "r") as f:
        template = Template(f.read())
    html_content = template.render(reset_link=reset_link)

    send_email(
        to_email=email,
        subject="Pecha Password Reset",
        message=html_content
    )


def _get_user_avatar(user: Users):
    return ""
