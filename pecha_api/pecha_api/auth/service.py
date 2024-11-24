from .models import CreateUserRequest
from ..users.models import Users
from ..db.database import SessionLocal
from .repository import get_hashed_password, save_user,get_user_by_email
from fastapi import HTTPException
from starlette import status


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