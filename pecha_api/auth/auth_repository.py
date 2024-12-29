import logging

import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from ..config import get_float, get
from ..users.users_models import Users

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password):
    if not password:
        return None
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as exception:
        logging.error(exception)
        return False


def create_access_token(data: dict, expires_delta: timedelta = None):
    if data is not None:
        if expires_delta is None:
            expires_delta = timedelta(minutes=get_float("ACCESS_TOKEN_EXPIRE_MINUTES"))
        return _generate_token(data, expires_delta)
    return None


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    if data is not None:
        if expires_delta is None:
            expires_delta = timedelta(days=get_float("REFRESH_TOKEN_EXPIRE_DAYS"))
        return _generate_token(data, expires_delta)
    return None


def _generate_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get("JWT_SECRET_KEY"), algorithm=get("JWT_ALGORITHM"))
    return encoded_jwt


def generate_token_data(user: Users):
    if not all([user.email, user.firstname, user.lastname]):
        return None
    data = {
        "sub": user.email,
        "name": user.firstname + " " + user.lastname,
        "iss": get("JWT_ISSUER"),
        "aud": get("JWT_AUD"),
        "iat": datetime.now(timezone.utc)
    }
    return data


def decode_token(token: str):
    return jwt.decode(token, get("JWT_SECRET_KEY"), algorithms=[get("JWT_ALGORITHM")], audience=get("JWT_AUD"))
