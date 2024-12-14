import jwt
from datetime import datetime, timezone, timedelta
from pecha_api.users.users_models import Users
from pecha_api.auth.auth_repository import (
    get_hashed_password, 
    verify_password,
    create_access_token,
    decode_token,
    create_refresh_token,
    generate_token_data
    
)
PECHA_JWT_ISSUER = "https://pecha.org"
PECHA_JWT_AUD = "https://pecha.org"


def test_verify_password_success():
    plain_password = "mysecretpassword"
    hashed_password = get_hashed_password(plain_password)
        
    assert verify_password(plain_password, hashed_password) == True


def test_verify_password_fail():
    plain_password = "mysecretpassword"
    hashed_password = get_hashed_password(plain_password)
        
    assert verify_password("wrongpassword", hashed_password) == False
    assert verify_password("wrongpassword", "wrongpassword") == False
    assert verify_password("wrongpassword", "") == False
    assert verify_password("wrongpassword", None) == False
    assert verify_password(None, "wrongpassword") == False
    assert verify_password("", "wrongpassword") == False
    assert verify_password("", hashed_password) == False
    assert verify_password(None, hashed_password) == False
    assert verify_password(plain_password, "") == False
    assert verify_password(plain_password, None) == False
    assert verify_password("", "") == False
    assert verify_password(None, None) == False
    assert verify_password("", None) == False
    assert verify_password(None, "") == False

    
def test_get_hashed_password():
    plain_password = "mysecretpassword"
    hashed_password = get_hashed_password(plain_password)
    
    assert hashed_password != plain_password
    assert verify_password(plain_password, hashed_password) == True


def test_get_hashed_password_empty_password():
    plain_password = ""
    hashed_password = get_hashed_password(plain_password)
    
    assert hashed_password == None


def test_get_hashed_password_none_password():
    plain_password = None
    hashed_password = get_hashed_password(plain_password)
    assert hashed_password == None


def test_get_hashed_password_different_passwords():
    plain_password1 = "mysecretpassword"
    plain_password2 = "anotherpassword"
    hashed_password1 = get_hashed_password(plain_password1)
    hashed_password2 = get_hashed_password(plain_password2)
    
    assert hashed_password1 != hashed_password2
    assert verify_password(plain_password1, hashed_password1) == True
    assert verify_password(plain_password2, hashed_password2) == True
    assert verify_password(plain_password1, hashed_password2) == False
    assert verify_password(plain_password2, hashed_password1) == False


def test_verify_password_with_valid_password():
    plain_password = "validpassword"
    hashed_password = get_hashed_password(plain_password)
        
    assert verify_password(plain_password, hashed_password) == True


def test_verify_password_with_invalid():
    plain_password = "validpassword"
    hashed_password = get_hashed_password(plain_password)

    assert verify_password("", hashed_password) == False 
    assert verify_password("invalidpassword", hashed_password) == False
    assert verify_password(None, hashed_password) == False
    assert verify_password(plain_password, "") == False
    assert verify_password(plain_password, None) == False
    assert verify_password("", "") == False
    assert verify_password(None, None) == False
    assert verify_password("", None) == False
    assert verify_password(None, "") == False


def test_create_access_token():
    data = {
        "sub": "test@example.com",
        "name":  "John Doe",
        "iss": PECHA_JWT_ISSUER,
        "aud": PECHA_JWT_AUD,
        "iat": datetime.now(timezone.utc)
    }
    token = create_access_token(data)
        
    assert token is not None
    decoded_data = decode_token(token)
    assert decoded_data["sub"] == "test@example.com"
    assert "exp" in decoded_data


def test_create_access_token_with_custom_expiry():
    data = {
        "sub": "test@example.com",
        "name":  "John Doe ",
        "iss": PECHA_JWT_ISSUER,
        "aud": PECHA_JWT_AUD,
        "iat": datetime.now(timezone.utc)
    }
    expires_delta = timedelta(minutes=10)
    token = create_access_token(data, expires_delta)
        
    assert token is not None
    decoded_data = decode_token(token)
    assert decoded_data["sub"] == "test@example.com"
    assert "exp" in decoded_data
    assert decoded_data["exp"] == int((datetime.now(timezone.utc) + expires_delta).timestamp())


def test_create_access_token_with_no_data():
    token = create_access_token(None)
        
    assert token is None


def test_create_refresh_token():
    data = {
        "sub": "test@example.com",
        "name":  "John Doe ",
        "iss": PECHA_JWT_ISSUER,
        "aud": PECHA_JWT_AUD,
        "iat": datetime.now(timezone.utc)
    }
    token = create_refresh_token(data)
            
    assert token is not None
    decoded_data = decode_token(token)
    assert decoded_data["sub"] == "test@example.com"
    assert "exp" in decoded_data


def test_create_refresh_token_with_custom_expiry():
    data = {
        "sub": "test@example.com",
        "name":  "John Doe ",
        "iss": PECHA_JWT_ISSUER,
        "aud": PECHA_JWT_AUD,
        "iat": datetime.now(timezone.utc)
    }
    expires_delta = timedelta(days=10)
    token = create_refresh_token(data, expires_delta)
            
    assert token is not None
    decoded_data = decode_token(token)
    assert decoded_data["sub"] == "test@example.com"
    assert "exp" in decoded_data
    assert decoded_data["exp"] == int((datetime.now(timezone.utc) + expires_delta).timestamp())


def test_create_refresh_token_with_no_data():
    token = create_refresh_token(None)
            
    assert token is None


def test_generate_token_data_success():
    user = Users(
        email="test@example.com", 
        firstname="John", 
        lastname="Doe"
        )
    token_data = generate_token_data(user)
        
    assert token_data is not None
    assert token_data["sub"] == "test@example.com"
    assert token_data["name"] == "John Doe"
    assert token_data["iss"] == PECHA_JWT_ISSUER
    assert token_data["aud"] == PECHA_JWT_AUD
    assert "iat" in token_data


def test_generate_token_data_missing_email():
    user = Users(
        email=None, 
        firstname="John", 
        lastname="Doe"
    )
    token_data = generate_token_data(user)
        
    assert token_data is None


def test_generate_token_data_missing_firstname():
    user = Users(
        email="test@example.com", 
        firstname=None, 
        lastname="Doe"
    )
    token_data = generate_token_data(user)
        
    assert token_data is None


def test_generate_token_data_missing_lastname():
    user = Users(
        email="test@example.com", 
        firstname="John", 
        lastname=None
    )
    token_data = generate_token_data(user)
        
    assert token_data is None


def test_generate_token_data_all_fields_missing():
    user = Users(email=None, firstname=None, lastname=None)
    token_data = generate_token_data(user)
        
    assert token_data is None


def test_decode_token_success():
    data = {
        "sub": "test@example.com",
        "name": "John Doe",
        "iss": PECHA_JWT_ISSUER,
        "aud": PECHA_JWT_AUD,
        "iat": datetime.now(timezone.utc)
    }
    token = create_access_token(data)
    decoded_data = decode_token(token)
        
    assert decoded_data is not None
    assert decoded_data["sub"] == "test@example.com"
    assert decoded_data["name"] == "John Doe"
    assert decoded_data["iss"] == PECHA_JWT_ISSUER
    assert decoded_data["aud"] == PECHA_JWT_AUD
    assert "exp" in decoded_data


def test_decode_token_invalid_signature():
    data = {
        "sub": "test@example.com",
        "name": "John Doe",
        "iss": PECHA_JWT_ISSUER,
        "aud": PECHA_JWT_AUD,
        "iat": datetime.now(timezone.utc)
    }
    token = create_access_token(data)
    invalid_token = token + "invalid"
        
    try:
        decode_token(invalid_token)
        assert False, "Expected jwt.exceptions.InvalidSignatureError"
    except jwt.exceptions.InvalidSignatureError:
        pass


def test_decode_token_expired():
    data = {
        "sub": "test@example.com",
        "name": "John Doe",
        "iss": PECHA_JWT_ISSUER,
        "aud": PECHA_JWT_AUD,
        "iat": datetime.now(timezone.utc)
    }
    expires_delta = timedelta(seconds=-1)
    token = create_access_token(data, expires_delta)
        
    try:
        decode_token(token)
        assert False, "Expected jwt.exceptions.ExpiredSignatureError"
    except jwt.exceptions.ExpiredSignatureError:
        pass


def test_decode_token_invalid_audience():
    data = {
        "sub": "test@example.com",
        "name": "John Doe",
        "iss": PECHA_JWT_ISSUER,
        "aud": "invalid_audience",
        "iat": datetime.now(timezone.utc)
    }
    token = create_access_token(data)
        
    try:
        decode_token(token)
        assert False, "Expected jwt.exceptions.InvalidAudienceError"
    except jwt.exceptions.InvalidAudienceError:
        pass


def test_decode_token_invalid_issuer():
    data = {
        "sub": "test@example.com",
        "name": "John Doe",
        "iss": "invalid_issuer",
        "aud": PECHA_JWT_AUD,
        "iat": datetime.now(timezone.utc)
    }
    token = create_access_token(data)
        
    try:
        decode_token(token)
    except jwt.exceptions.InvalidIssuerError:
        assert False, "Expected jwt.exceptions.InvalidIssuerError"