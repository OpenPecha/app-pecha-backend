import uuid
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from starlette import status
from jose import jwt

from pecha_api.plans.auth.plan_auth_services import (
    register_author,
    _validate_password,
    _generate_author_verification_token,
    verify_author_email,
)
from pecha_api.plans.auth.plan_auth_model import CreateAuthorRequest
from pecha_api.plans.response_message import (
    PASSWORD_EMPTY,
    PASSWORD_LENGTH_INVALID,
    TOKEN_TYPE_INVALID,
    TOKEN_PAYLOAD_INVALID,
    TOKEN_EXPIRED,
    TOKEN_INVALID,
    EMAIL_ALREADY_VERIFIED,
    EMAIL_VERIFIED_SUCCESS,
    REGISTRATION_MESSAGE,
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
        patch("pecha_api.plans.auth.plan_auth_services._send_verification_email") as mock_send_email:
        _mock_session_local(mock_session_local)

        mock_save_author.return_value = saved_author
        mock_get_hashed_password.return_value = "hashed_password123"

        response = register_author(create_user_request=create_request)

        mock_get_hashed_password.assert_called_once_with(create_request.password)
        mock_save_author.assert_called_once_with(db=ANY, author=ANY)
        mock_send_email.assert_called_once_with(email=create_request.email)

        assert response is not None
        assert response.author.first_name == saved_author.first_name
        assert response.author.last_name == saved_author.last_name
        assert response.author.email == saved_author.email
        assert response.author.status == AuthorStatus.PENDING_VERIFICATION
        assert response.author.message == REGISTRATION_MESSAGE


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

    with patch("pecha_api.plans.auth.plan_auth_services.get", return_value="x"), \
        patch("pecha_api.plans.auth.plan_auth_services.jwt.decode", return_value=payload) as mock_decode, \
        patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email") as mock_get_author_by_email, \
        patch("pecha_api.plans.auth.plan_auth_services.update_author") as mock_update_author:
        _mock_session_local(mock_session_local)
        mock_get_author_by_email.return_value = author

        response = verify_author_email(token)

        mock_decode.assert_called_once()
        mock_get_author_by_email.assert_called_once_with(db=ANY, email=payload["email"])
        mock_update_author.assert_called_once_with(db=ANY, author=author)
        assert response == {"message": EMAIL_VERIFIED_SUCCESS}


def test_verify_author_email_already_verified():
    token = "valid_token"
    payload = {
        "email": "john.doe@example.com",
        "typ": "author_email_verification",
    }

    author = MagicMock()
    author.is_verified = True

    with patch("pecha_api.plans.auth.plan_auth_services.get", return_value="x"), \
        patch("pecha_api.plans.auth.plan_auth_services.jwt.decode", return_value=payload), \
        patch("pecha_api.plans.auth.plan_auth_services.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.auth.plan_auth_services.get_author_by_email") as mock_get_author_by_email, \
        patch("pecha_api.plans.auth.plan_auth_services.update_author") as mock_update_author:
        _mock_session_local(mock_session_local)
        mock_get_author_by_email.return_value = author

        response = verify_author_email(token)

        mock_update_author.assert_not_called()
        assert response == {"message": EMAIL_ALREADY_VERIFIED}


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
            assert e.detail == TOKEN_TYPE_INVALID


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
            assert e.detail == TOKEN_PAYLOAD_INVALID


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

from pecha_api.plans.plan_auth.plan_auth_services import (
    authenticate_author,
    check_verified_author,
    authenticate_and_generate_tokens,
    generate_token_author,
)
from pecha_api.plans.plan_auth.plan_auth_model import AuthorInfo, TokenResponse, AuthorLoginResponse


def test_authenticate_author_success():
    author = MagicMock()
    author.password = "hashed"
    author.is_verified = True
    author.is_active = True

    with patch("pecha_api.plans.plan_auth.plan_auth_services.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.plan_auth.plan_auth_services.get_author_by_email", return_value=author), \
        patch("pecha_api.plans.plan_auth.plan_auth_services.verify_password", return_value=True):
        _mock_session_local(mock_session_local)

        result = authenticate_author("test@example.com", "password")
        assert result == author


def test_authenticate_author_invalid_password():
    author = MagicMock()
    author.password = "hashed"
    author.is_verified = True
    author.is_active = True

    with patch("pecha_api.plans.plan_auth.plan_auth_services.SessionLocal") as mock_session_local, \
        patch("pecha_api.plans.plan_auth.plan_auth_services.get_author_by_email", return_value=author), \
        patch("pecha_api.plans.plan_auth.plan_auth_services.verify_password", return_value=False):
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
    with patch("pecha_api.plans.plan_auth.plan_auth_services.authenticate_author", return_value=author), \
        patch("pecha_api.plans.plan_auth.plan_auth_services.generate_token_author", return_value="tokens") as mock_gen:
        result = authenticate_and_generate_tokens("email", "password")
        mock_gen.assert_called_once_with(author)
        assert result == "tokens"


def test_generate_token_author_builds_response():
    author = MagicMock()
    author.first_name = "John"
    author.last_name = "Doe"
    author.image_url = "img.png"

    with patch("pecha_api.plans.plan_auth.plan_auth_services.generate_token_data", return_value={"sub": "123"}), \
        patch("pecha_api.plans.plan_auth.plan_auth_services.create_access_token", return_value="access"), \
        patch("pecha_api.plans.plan_auth.plan_auth_services.create_refresh_token", return_value="refresh"):
        result = generate_token_author(author)

        assert isinstance(result, AuthorLoginResponse)
        assert isinstance(result.user, AuthorInfo)
        assert isinstance(result.auth, TokenResponse)
        assert result.auth.access_token == "access"
        assert result.auth.refresh_token == "refresh"
        assert result.user.name == "John Doe"
        assert result.user.image_url == "img.png"

