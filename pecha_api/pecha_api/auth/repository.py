from typing import Optional
import jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta,timezone

from ..users.models import Users

SECRET_KEY = "oJvUxI5jY7nXaD4sC_kFGoM0_qAuewVxg3p6F8CH-tI"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30
PECHA_JWT_ISSUER = "https://pecha.org"
PECHA_JWT_AUD = "https://pecha.org"  # Replace with your actual audience

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


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def generate_token_data(user: Users):
    data = {
        "sub": user.email,
        "name": user.firstname + " " + user.lastname,
        "username": user.username,
        "iss": PECHA_JWT_ISSUER,
        "aud": PECHA_JWT_AUD,
        "iat": datetime.now(timezone.utc)
    }
    return data


def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],audience=PECHA_JWT_AUD)
