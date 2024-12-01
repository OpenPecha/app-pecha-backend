import jwt
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

def get_hashed_password(password):
    if not password:
        return None
    try:
        return pwd_context.hash(password)
    except Exception as e:
        return None


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta = None):
    if data is not None:
        if expires_delta is None:
            expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        return _generate_token(data, expires_delta)
    return None

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    if data is not None:
        if expires_delta is None:
            expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        return _generate_token(data, expires_delta)
    return None

def _generate_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_token_data(user: Users):
    if not all([user.email, user.firstname, user.lastname]):
        return None
    data = {
        "sub": user.email,
        "name": user.firstname + " " + user.lastname,
        "iss": PECHA_JWT_ISSUER,
        "aud": PECHA_JWT_AUD,
        "iat": datetime.now(timezone.utc)
    }
    return data


def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],audience=PECHA_JWT_AUD)