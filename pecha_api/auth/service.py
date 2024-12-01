from .models import CreateUserRequest,UserLoginResponse,RefreshTokenResponse
from ..users.models import Users
from ..db.database import SessionLocal
from ..users.repository import get_user_by_email, save_user, get_user_by_username
from .repository import get_hashed_password, verify_password, create_access_token, create_refresh_token, generate_token_data,decode_token
from .enums import RegistrationSource
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette import status
import jwt


def create_user(create_user_request: CreateUserRequest, registration_source: RegistrationSource):
    db_session = SessionLocal()
    try:
        validate_user_already_exist(email=create_user_request.email, username=create_user_request.username)
        new_user = Users(**create_user_request.model_dump())
        if registration_source == RegistrationSource.EMAIL:
            validate_password(new_user.password)
            hashed_password = get_hashed_password(new_user.password)
            new_user.password = hashed_password
        new_user.registration_source = registration_source.value
        save_user(db=db_session, user=new_user)
    finally:
        db_session.close()

def validate_password(password: str):
    if not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password cannot be empty")
    if len(password) < 8 or len(password) > 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be between 8 and 20 characters")
    

def validate_user_already_exist(email: str, username: str):
    db_session = SessionLocal()
    try:
        existing_user_by_email = get_user_by_email(db=db_session, email=email)
        existing_user_by_username = get_user_by_username(db=db_session, username=username)
        if existing_user_by_email or existing_user_by_username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email or username already exists')
    finally:
        db_session.close()

def authenticate_and_generate_tokens(email: str, password: str):
    try:
        user = authenticate_user(email=email, password=password)
        data = generate_token_data(user)
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        return UserLoginResponse(
            access_token=access_token, 
            refresh_token=refresh_token, 
            token_type="Bearer"
        )
    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code,
                            content={"message": exception.detail})


def authenticate_user(email: str, password: str):
    db_session = SessionLocal()
    try:
        user = get_user_by_email(db=db_session, email=email)

        if not user or not verify_password(
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
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
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