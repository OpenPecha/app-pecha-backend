from .models import CreateUserRequest,UserLoginResponse,RefreshTokenResponse
from ..users.models import Users
from ..db.database import SessionLocal
from .repository import get_user_by_email, save_user, get_hashed_password, verify_password, create_access_token, create_refresh_token, generate_token_data,decode_token
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette import status
import jwt


def create_user(create_user_request: CreateUserRequest):
    db_session = SessionLocal()
    try:
        exising_user = get_user_by_email(db=db_session, email=create_user_request.email)
        if exising_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail='Email or password is not match')
        new_user = Users(**create_user_request.model_dump())
        hashed_password = get_hashed_password(new_user.password)
        new_user.password = hashed_password
        save_user(db=db_session, user=new_user)
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