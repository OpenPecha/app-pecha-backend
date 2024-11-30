from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
import jwt
import pytest
from passlib.context import CryptContext
from ...pecha_api.users.models import Users

from ..auth.repository import (
    save_user, get_user_by_email, get_hashed_password, verify_password,
    create_access_token, create_refresh_token, generate_token_data, decode_token,
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS,
    PECHA_JWT_ISSUER, PECHA_JWT_AUD
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_save_user():
    db = MagicMock()
    user = Users(email="test@example.com")
    save_user(db, user)
    db.add.assert_called_once_with(user)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user)

def test_get_user_by_email():
    db = MagicMock()
    email = "test@example.com"
    get_user_by_email(db, email)
    db.query.assert_called_once()
    db.query().filter.assert_called_once_with(Users.email == email)
    db.query().filter().first.assert_called_once()

def test_get_hashed_password():
    password = "password123"
    hashed_password = get_hashed_password(password)
    assert pwd_context.verify(password, hashed_password)

def test_verify_password():
    password = "password123"
    hashed_password = pwd_context.hash(password)
    assert verify_password(password, hashed_password)

def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=PECHA_JWT_AUD)
    assert decoded["sub"] == data["sub"]

def test_create_refresh_token():
    data = {"sub": "test@example.com"}
    token = create_refresh_token(data)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=PECHA_JWT_AUD)
    assert decoded["sub"] == data["sub"]

def test_generate_token_data():
    user = Users(email="test@example.com", firstname="Test", lastname="User", username="testuser")
    data = generate_token_data(user)
    assert data["sub"] == user.email
    assert data["name"] == user.firstname + " " + user.lastname
    assert data["username"] == user.username
    assert data["iss"] == PECHA_JWT_ISSUER
    assert data["aud"] == PECHA_JWT_AUD
    assert "iat" in data

def test_decode_token():
    data = {"sub": "test@example.com"}
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    decoded = decode_token(token)
    assert decoded["sub"] == data["sub"]