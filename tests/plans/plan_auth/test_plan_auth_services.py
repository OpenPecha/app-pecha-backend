import uuid
import json
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette import status
from jose import jwt

from pecha_api.plans.auth.plan_auth_services import (
    register_author,
    _validate_password,
    _generate_author_verification_token,
    verify_author_email,
    request_reset_password,
    update_password,
)
from pecha_api.plans.auth.plan_auth_models import CreateAuthorRequest, AuthorVerificationResponse
from pecha_api.plans.response_message import (
    PASSWORD_EMPTY,
    PASSWORD_LENGTH_INVALID,
    TOKEN_EXPIRED,
    EMAIL_ALREADY_VERIFIED,
    EMAIL_VERIFIED_SUCCESS,
    REGISTRATION_MESSAGE, TOKEN_INVALID,
    BAD_REQUEST,
    AUTHOR_ALREADY_EXISTS,
)
from pecha_api.plans.auth.plan_auth_enums import AuthorStatus


def _mock_session_local(mock_session_local):
    mock_db_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db_session
    mock_session_local.return_value.__exit__.return_value = False
    return mock_db_session


def test_register_author_success():
    create_request = CreateAuthorRequest(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="password123",
    )

    saved_author = MagicMock()
    saved_author.id = uuid.uuid4()
    saved_author.first_name = create_request.first_name
    saved_author.last_name = create_request.last_name
    saved_author.email = create_request.email
    saved_author.status = AuthorStatus.PENDING_VERIFICATION
    saved_author.is_verified = False
    saved_author.created_at = datetime.now(timezone.utc)
    saved_author.created_by = create_request.email

    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.auth.plan_auth_services.save_author") as mock_save_author, \
        patch("pecha_api.plans.auth.plan_auth_services.get_hashed_password") as mock_get_hashed_password, \
        patch("pecha_api.plans.auth.plan_auth_services._send_verification_email") as mock_send_email, \
        patch("pecha_api.plans.auth.plan_auth_services.check_author_exists", return_value=False) as mock_check_exists:
        _mock_session_local(mock_session_local)

        mock_save_author.return_value = saved_author
        mock_get_hashed_password.return_value = "hashed_password123"

        response = register_author(create_user_request=create_request)

        mock_get_hashed_password.assert_called_once_with(create_request.password)
        mock_save_author.assert_called_once_with(db=ANY, author=ANY)
        mock_send_email.assert_called_once_with(email=create_request.email)
        mock_check_exists.assert_called_once_with(db=ANY, email=create_request.email)

        assert response is not None
        assert response.first_name == saved_author.first_name
        assert response.last_name == saved_author.last_name
        assert response.email == saved_author.email
        assert response.status == AuthorStatus.PENDING_VERIFICATION
        assert response.message == REGISTRATION_MESSAGE


def test_register_author_duplicate_still_proceeds():
    create_request = CreateAuthorRequest(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="password123",
    )

    saved_author = MagicMock()
    saved_author.id = uuid.uuid4()
    saved_author.first_name = create_request.first_name
    saved_author.last_name = create_request.last_name
    saved_author.email = create_request.email
    saved_author.status = AuthorStatus.PENDING_VERIFICATION
    saved_author.is_verified = False
    saved_author.created_at = datetime.now(timezone.utc)
    saved_author.created_by = create_request.email

    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.auth.plan_auth_services.check_author_exists", return_value=True) as mock_check_exists, \
        patch("pecha_api.plans.auth.plan_auth_services.save_author") as mock_save_author, \
        patch("pecha_api.plans.auth.plan_auth_services.get_hashed_password") as mock_get_hashed_password, \
        patch("pecha_api.plans.auth.plan_auth_services._send_verification_email") as mock_send_email:
        _mock_session_local(mock_session_local)

        mock_save_author.return_value = saved_author
        mock_get_hashed_password.return_value = "hashed_password123"

        response = register_author(create_user_request=create_request)

        mock_check_exists.assert_called_once_with(db=ANY, email=create_request.email)
        mock_get_hashed_password.assert_called_once_with(create_request.password)
        mock_save_author.assert_called_once_with(db=ANY, author=ANY)
        mock_send_email.assert_called_once_with(email=create_request.email)

        assert response is not None
        assert response.first_name == saved_author.first_name
        assert response.last_name == saved_author.last_name
        assert response.email == saved_author.email
        assert response.status == AuthorStatus.PENDING_VERIFICATION
        assert response.message == REGISTRATION_MESSAGE


def test__validate_password_empty_password():
    password = ""

    try:
        _validate_password(password)
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST
        assert e.detail == PASSWORD_EMPTY


def test__validate_password_short_password():
    password = "short"

    try:
        _validate_password(password)
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST
        assert e.detail == PASSWORD_LENGTH_INVALID


def test__validate_password_long_password():
    password = "a" * 21

    try:
        _validate_password(password)
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST
        assert e.detail == PASSWORD_LENGTH_INVALID


def test__validate_password_valid_password():
    _validate_password("validpass")


def test__generate_author_verification_token_and_decode():
    email = "john.doe@example.com"

    def fake_get(key: str):
        mapping = {
            "JWT_ISSUER": "pecha",
            "JWT_AUD": "pecha-users",
            "JWT_SECRET_KEY": "secret-key",
            "JWT_ALGORITHM": "HS256",
        }
        return mapping[key]

    with patch("pecha_api.plans.auth.plan_auth_services.get", side_effect=fake_get):
        token = _generate_author_verification_token(email)
        assert isinstance(token, str) and len(token) > 0

        payload = jwt.decode(
            token,
            fake_get("JWT_SECRET_KEY"),
            algorithms=[fake_get("JWT_ALGORITHM")],
            audience=fake_get("JWT_AUD"),
        )
        assert payload["email"] == email
        assert payload["iss"] == fake_get("JWT_ISSUER")
        assert payload["aud"] == fake_get("JWT_AUD")
        assert payload["typ"] == "author_email_verification"
        assert datetime.fromtimestamp(payload["exp"], tz=timezone.utc) > datetime.now(timezone.utc)


def test_verify_author_email_success():
    token = "valid_token"
    payload = {
        "email": "john.doe@example.com",
        "typ": "author_email_verification",
    }

    author = MagicMock()
    author.is_verified = False
    author.email = "john.doe@example.com"

    with patch("pecha_api.plans.auth.plan_auth_services.get", return_value="x"), \
        patch("pecha_api.plans.auth.plan_auth_services.jwt.decode", return_value=payload) as mock_decode, \
        patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email") as mock_get_author_by_email, \
        patch("pecha_api.plans.auth.plan_auth_services.update_author") as mock_update_author:
        _mock_session_local(mock_session_local)
        mock_get_author_by_email.return_value = author

        response: AuthorVerificationResponse = verify_author_email(token)

        mock_decode.assert_called_once()
        mock_get_author_by_email.assert_called_once_with(db=ANY, email=payload["email"])
        mock_update_author.assert_called_once_with(db=ANY, author=author)
        assert response.email == "john.doe@example.com"
        assert response.status == AuthorStatus.INACTIVE
        assert response.message == EMAIL_VERIFIED_SUCCESS


def test_verify_author_email_already_verified():
    token = "valid_token"
    payload = {
        "email": "john.doe@example.com",
        "typ": "author_email_verification",
    }

    author = MagicMock()
    author.is_verified = True
    author.email = "john.doe@example.com"

    with patch("pecha_api.plans.auth.plan_auth_services.get", return_value="x"), \
        patch("pecha_api.plans.auth.plan_auth_services.jwt.decode", return_value=payload), \
        patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email") as mock_get_author_by_email, \
        patch("pecha_api.plans.auth.plan_auth_services.update_author") as mock_update_author:
        _mock_session_local(mock_session_local)
        mock_get_author_by_email.return_value = author

        response: AuthorVerificationResponse  = verify_author_email(token)

        mock_update_author.assert_not_called()
        assert response.email == "john.doe@example.com"
        assert response.status == AuthorStatus.INACTIVE
        assert response.message == EMAIL_ALREADY_VERIFIED


def test_verify_author_email_invalid_type():
    token = "valid_token"
    payload = {
        "email": "john.doe@example.com",
        "typ": "wrong_type",
    }

    with patch("pecha_api.plans.auth.plan_auth_services.get", return_value="x"), \
        patch("pecha_api.plans.auth.plan_auth_services.jwt.decode", return_value=payload):
        try:
            verify_author_email(token)
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == TOKEN_INVALID


def test_verify_author_email_missing_email():
    token = "valid_token"
    payload = {
        "typ": "author_email_verification",
    }

    with patch("pecha_api.plans.auth.plan_auth_services.get", return_value="x"), \
        patch("pecha_api.plans.auth.plan_auth_services.jwt.decode", return_value=payload):
        try:
            verify_author_email(token)
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == TOKEN_INVALID


def test_verify_author_email_expired_token():
    token = "expired_token"

    with patch("pecha_api.plans.auth.plan_auth_services.get", return_value="x"), \
        patch("pecha_api.plans.auth.plan_auth_services.jwt.decode") as mock_decode:
        mock_decode.side_effect = jwt.ExpiredSignatureError

        try:
            verify_author_email(token)
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == TOKEN_EXPIRED



def test_send_verification_email_sends_email():
    from pecha_api.plans.auth.plan_auth_services import _send_verification_email

    with patch("pecha_api.plans.auth.plan_auth_services._generate_author_verification_token", return_value="tok"), \
        patch("pecha_api.plans.auth.plan_auth_services.get", side_effect=lambda k: "http://backend" if k == "PECHA_BACKEND_ENDPOINT" else "x"), \
        patch("pecha_api.plans.auth.plan_auth_services.Template.render") as mock_render, \
        patch("pecha_api.plans.auth.plan_auth_services.send_email") as mock_send_email:
        mock_render.return_value = "rendered_html"

        _send_verification_email("john.doe@example.com")

        mock_render.assert_called_once()
        mock_send_email.assert_called_once_with(
            to_email="john.doe@example.com",
            subject="Verify your Pecha account",
            message="rendered_html",
        )

from pecha_api.plans.auth.plan_auth_services import (
    authenticate_author,
    check_verified_author,
    authenticate_and_generate_tokens,
    generate_token_author,
    generate_author_token_data,
)
from pecha_api.plans.auth.plan_auth_models import AuthorInfo, TokenResponse, AuthorLoginResponse


def test_authenticate_author_success():
    author = MagicMock()
    author.password = "hashed"
    author.is_verified = True
    author.is_active = True

    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email", return_value=author), \
        patch("pecha_api.plans.auth.plan_auth_services.verify_password", return_value=True):
        _mock_session_local(mock_session_local)

        result = authenticate_author("test@example.com", "password")
        assert result == author


def test_authenticate_author_invalid_password():
    author = MagicMock()
    author.password = "hashed"
    author.is_verified = True
    author.is_active = True

    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email", return_value=author), \
        patch("pecha_api.plans.auth.plan_auth_services.verify_password", return_value=False):
        _mock_session_local(mock_session_local)

        try:
            authenticate_author("test@example.com", "wrong")
        except HTTPException as e:
            assert e.status_code == status.HTTP_401_UNAUTHORIZED
            assert e.detail == "Invalid email or password"


def test_check_verified_author_not_verified():
    author = MagicMock(is_verified=False, is_active=True)
    try:
        check_verified_author(author)
    except HTTPException as e:
        assert e.status_code == status.HTTP_401_UNAUTHORIZED
        assert e.detail == "Author not verified"


def test_check_verified_author_not_active():
    author = MagicMock(is_verified=True, is_active=False)
    try:
        check_verified_author(author)
    except HTTPException as e:
        assert e.status_code == status.HTTP_401_UNAUTHORIZED
        assert e.detail == "Author not active"


def test_check_verified_author_valid():
    author = MagicMock(is_verified=True, is_active=True)
    # Should not raise
    check_verified_author(author)


def test_authenticate_and_generate_tokens():
    author = MagicMock()
    with patch("pecha_api.plans.auth.plan_auth_services.authenticate_author", return_value=author), \
        patch("pecha_api.plans.auth.plan_auth_services.generate_token_author", return_value="tokens") as mock_gen:
        result = authenticate_and_generate_tokens("email", "password")
        mock_gen.assert_called_once_with(author)
        assert result == "tokens"


def test_generate_token_author_builds_response():
    author = MagicMock()
    author.first_name = "John"
    author.last_name = "Doe"
    author.email = "john.doe@example.com"
    author.image_url = "img.png"

    with patch("pecha_api.plans.auth.plan_auth_services.generate_author_token_data", return_value={"sub": "123"}), \
        patch("pecha_api.plans.auth.plan_auth_services.create_access_token", return_value="access"), \
        patch("pecha_api.plans.auth.plan_auth_services.create_refresh_token", return_value="refresh"):
        result = generate_token_author(author)

        assert isinstance(result, AuthorLoginResponse)
        assert isinstance(result.user, AuthorInfo)
        assert isinstance(result.auth, TokenResponse)
        assert result.auth.access_token == "access"
        assert result.auth.refresh_token == "refresh"
        assert result.user.name == "John Doe"
        assert result.user.image_url == "img.png"

def test_request_reset_password_success():
    email = "john.doe@example.com"
    
    mock_author = MagicMock()
    mock_author.email = email
    
    mock_password_reset = MagicMock()
    
    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email", return_value=mock_author) as mock_get_author, \
         patch("pecha_api.plans.auth.plan_auth_services.save_password_reset") as mock_save_reset, \
         patch("pecha_api.plans.auth.plan_auth_services.send_reset_email") as mock_send_email, \
         patch("pecha_api.plans.auth.plan_auth_services.secrets.token_urlsafe", return_value="test_token_123") as mock_token, \
         patch("pecha_api.plans.auth.plan_auth_services.get", return_value="https://example.com") as mock_get_config:
        
        mock_db_session = _mock_session_local(mock_session_local)
        
        result = request_reset_password(email=email)
        
        mock_get_author.assert_called_once_with(db=mock_db_session, email=email)
        mock_save_reset.assert_called_once()
        mock_send_email.assert_called_once_with(
            email=email, 
            reset_link="https://example.com/reset-password?token=test_token_123"
        )
        
        assert result == {"message": "If the email exists in our system, a password reset email has been sent."}


def test_request_reset_password_author_not_found():
    email = "nonexistent@example.com"
    
    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email") as mock_get_author:
        
        _mock_session_local(mock_session_local)
        mock_get_author.side_effect = HTTPException(status_code=404, detail="Author not found")
        
        try:
            request_reset_password(email=email)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == 404
            assert e.detail == "Author not found"


def test_request_reset_password_database_error():
    email = "john.doe@example.com"
    
    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email") as mock_get_author:
        
        _mock_session_local(mock_session_local)
        mock_get_author.side_effect = Exception("Database connection error")
        
        try:
            request_reset_password(email=email)
            assert False, "Expected Exception to be raised"
        except Exception as e:
            assert str(e) == "Database connection error"


def test_request_reset_password_email_send_failure():
    email = "john.doe@example.com"
    
    mock_author = MagicMock()
    mock_author.email = email
    
    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email", return_value=mock_author), \
         patch("pecha_api.plans.auth.plan_auth_services.save_password_reset"), \
         patch("pecha_api.plans.auth.plan_auth_services.send_reset_email") as mock_send_email, \
         patch("pecha_api.plans.auth.plan_auth_services.secrets.token_urlsafe", return_value="test_token_123"), \
         patch("pecha_api.plans.auth.plan_auth_services.get", return_value="https://example.com"):
        
        _mock_session_local(mock_session_local)
        mock_send_email.side_effect = Exception("Email service unavailable")
        
        try:
            request_reset_password(email=email)
            assert False, "Expected Exception to be raised"
        except Exception as e:
            assert str(e) == "Email service unavailable"


def test_update_password_success():
    token = "valid_reset_token"
    new_password = "newpassword123"
    email = "john.doe@example.com"
    
    mock_reset_entry = MagicMock()
    mock_reset_entry.email = email
    mock_reset_entry.token_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)  # Valid expiry
    
    mock_author = MagicMock()
    mock_author.email = email
    mock_author.registration_source = 'email'
    
    mock_updated_author = MagicMock()
    mock_updated_author.email = email
    mock_updated_author.password = "hashed_new_password"
    
    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.auth.plan_auth_services.get_password_reset_by_token", return_value=mock_reset_entry) as mock_get_reset, \
         patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email", return_value=mock_author) as mock_get_author, \
         patch("pecha_api.plans.auth.plan_auth_services._validate_password") as mock_validate, \
         patch("pecha_api.plans.auth.plan_auth_services.get_hashed_password", return_value="hashed_new_password") as mock_hash, \
         patch("pecha_api.plans.auth.plan_auth_services.save_author", return_value=mock_updated_author) as mock_save:
        
        mock_db_session = _mock_session_local(mock_session_local)
        
        result = update_password(token=token, password=new_password)
        
        mock_get_reset.assert_called_once_with(db=mock_db_session, token=token)
        mock_get_author.assert_called_once_with(db=mock_db_session, email=email)
        mock_validate.assert_called_once_with(new_password)
        mock_hash.assert_called_once_with(new_password)
        mock_save.assert_called_once_with(db=mock_db_session, author=mock_author)
        
        assert mock_author.password == "hashed_new_password"
        assert result == mock_updated_author


def test_update_password_invalid_token():
    token = "invalid_token"
    new_password = "newpassword123"
    
    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.auth.plan_auth_services.get_password_reset_by_token", return_value=None) as mock_get_reset:
        
        _mock_session_local(mock_session_local)
        
        try:
            update_password(token=token, password=new_password)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == "Invalid or expired token"


def test_update_password_expired_token():
    token = "expired_token"
    new_password = "newpassword123"
    
    mock_reset_entry = MagicMock()
    mock_reset_entry.email = "john.doe@example.com"
    mock_reset_entry.token_expiry = datetime.now(timezone.utc) - timedelta(minutes=10)
    
    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.auth.plan_auth_services.get_password_reset_by_token", return_value=mock_reset_entry):
        
        _mock_session_local(mock_session_local)
        
        try:
            update_password(token=token, password=new_password)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == "Invalid or expired token"


def test_update_password_registration_source_mismatch():
    token = "valid_reset_token"
    new_password = "newpassword123"
    email = "john.doe@example.com"
    
    mock_reset_entry = MagicMock()
    mock_reset_entry.email = email
    mock_reset_entry.token_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    mock_author = MagicMock()
    mock_author.email = email
    mock_author.registration_source = 'google'
    
    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.auth.plan_auth_services.get_password_reset_by_token", return_value=mock_reset_entry), \
         patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email", return_value=mock_author):
        
        _mock_session_local(mock_session_local)
        
        try:
            update_password(token=token, password=new_password)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == "Registration Source Mismatch"


def test_update_password_weak_password():
    token = "valid_reset_token"
    new_password = "weak"  # Too short
    email = "john.doe@example.com"
    
    mock_reset_entry = MagicMock()
    mock_reset_entry.email = email
    mock_reset_entry.token_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    mock_author = MagicMock()
    mock_author.email = email
    mock_author.registration_source = 'email'
    
    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.auth.plan_auth_services.get_password_reset_by_token", return_value=mock_reset_entry), \
         patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email", return_value=mock_author), \
         patch("pecha_api.plans.auth.plan_auth_services._validate_password") as mock_validate:
        
        _mock_session_local(mock_session_local)
        mock_validate.side_effect = HTTPException(status_code=400, detail="Password must be between 8 and 20 characters")
        
        try:
            update_password(token=token, password=new_password)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "Password must be between 8 and 20 characters"


def test_update_password_author_not_found():
    token = "valid_reset_token"
    new_password = "newpassword123"
    email = "nonexistent@example.com"
    
    mock_reset_entry = MagicMock()
    mock_reset_entry.email = email
    mock_reset_entry.token_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.auth.plan_auth_services.get_password_reset_by_token", return_value=mock_reset_entry), \
         patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email") as mock_get_author:
        
        _mock_session_local(mock_session_local)
        mock_get_author.side_effect = HTTPException(status_code=404, detail="Author not found")
        
        try:
            update_password(token=token, password=new_password)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == 404
            assert e.detail == "Author not found"


def test_update_password_database_save_error():
    token = "valid_reset_token"
    new_password = "newpassword123"
    email = "john.doe@example.com"
    
    mock_reset_entry = MagicMock()
    mock_reset_entry.email = email
    mock_reset_entry.token_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    mock_author = MagicMock()
    mock_author.email = email
    mock_author.registration_source = 'email'
    
    with patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
         patch("pecha_api.plans.auth.plan_auth_services.get_password_reset_by_token", return_value=mock_reset_entry), \
         patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email", return_value=mock_author), \
         patch("pecha_api.plans.auth.plan_auth_services._validate_password"), \
         patch("pecha_api.plans.auth.plan_auth_services.get_hashed_password", return_value="hashed_password"), \
         patch("pecha_api.plans.auth.plan_auth_services.save_author") as mock_save:
        
        _mock_session_local(mock_session_local)
        mock_save.side_effect = Exception("Database save failed")
        
        try:
            update_password(token=token, password=new_password)
            assert False, "Expected Exception to be raised"
        except Exception as e:
            assert str(e) == "Database save failed"


def test_generate_author_token_data_success():
    author = MagicMock()
    author.email = "john.doe@example.com"
    author.first_name = "John"
    author.last_name = "Doe"
    
    with patch("pecha_api.plans.auth.plan_auth_services.get") as mock_get, \
         patch("pecha_api.plans.auth.plan_auth_services.datetime") as mock_datetime:
        
        mock_get.side_effect = lambda key: {
            "JWT_ISSUER": "https://pecha.org",
            "JWT_AUD": "https://pecha.org"
        }[key]
        
        mock_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now
        mock_datetime.timezone = timezone
        
        result = generate_author_token_data(author)
        
        assert result is not None
        assert result["email"] == "john.doe@example.com"
        assert result["name"] == "John Doe"
        assert result["iss"] == "https://pecha.org"
        assert result["aud"] == "https://pecha.org"
        assert result["iat"] == mock_now


def test_generate_author_token_data_missing_email():
    author = MagicMock()
    author.email = None
    author.first_name = "John"
    author.last_name = "Doe"
    
    result = generate_author_token_data(author)
    
    assert result is None


def test_generate_author_token_data_empty_email():
    author = MagicMock()
    author.email = ""
    author.first_name = "John"
    author.last_name = "Doe"
    
    result = generate_author_token_data(author)
    
    assert result is None


def test_generate_author_token_data_missing_first_name():
    author = MagicMock()
    author.email = "john.doe@example.com"
    author.first_name = None
    author.last_name = "Doe"
    
    result = generate_author_token_data(author)
    
    assert result is None


def test_generate_author_token_data_empty_first_name():
    author = MagicMock()
    author.email = "john.doe@example.com"
    author.first_name = ""
    author.last_name = "Doe"
    
    result = generate_author_token_data(author)
    
    assert result is None


def test_generate_author_token_data_missing_last_name():
    author = MagicMock()
    author.email = "john.doe@example.com"
    author.first_name = "John"
    author.last_name = None
    
    result = generate_author_token_data(author)
    
    assert result is None


def test_generate_author_token_data_empty_last_name():
    author = MagicMock()
    author.email = "john.doe@example.com"
    author.first_name = "John"
    author.last_name = ""
    
    result = generate_author_token_data(author)
    
    assert result is None


def test_generate_author_token_data_all_fields_missing():
    author = MagicMock()
    author.email = None
    author.first_name = None
    author.last_name = None
    
    result = generate_author_token_data(author)
    
    assert result is None


def test_generate_author_token_data_with_whitespace_names():
    author = MagicMock()
    author.email = "john.doe@example.com"
    author.first_name = " John "
    author.last_name = " Doe "
    
    with patch("pecha_api.plans.auth.plan_auth_services.get") as mock_get, \
         patch("pecha_api.plans.auth.plan_auth_services.datetime") as mock_datetime:
        
        mock_get.side_effect = lambda key: {
            "JWT_ISSUER": "https://pecha.org",
            "JWT_AUD": "https://pecha.org"
        }[key]
        
        mock_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now
        mock_datetime.timezone = timezone
        
        result = generate_author_token_data(author)
        
        assert result is not None
        assert result["name"] == " John   Doe "
        assert result["email"] == "john.doe@example.com"