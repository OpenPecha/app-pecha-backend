import uuid
import jwt
from unittest.mock import patch, MagicMock, ANY

from starlette import status

from pecha_api.auth.auth_service import (
    register_user_with_source,
    generate_token_user,
    authenticate_user,
    get_hashed_password,
    refresh_access_token,
    _create_user,
    validate_user_already_exist,
    authenticate_and_generate_tokens
)
from pecha_api.auth.auth_models import CreateUserRequest
from pecha_api.auth.auth_enums import RegistrationSource
from fastapi import HTTPException
import json


def test_register_user_with_email_success():
    create_user_request = CreateUserRequest(
        firstname="John",
        lastname="Doe",
        email="test@example.com",
        password="password123"
    )
    registration_source = RegistrationSource.EMAIL

    with patch('pecha_api.auth.auth_service._create_user') as mock_create_user, \
            patch('pecha_api.auth.auth_service.generate_token_user') as mock_generate_token_user:
        mock_user = MagicMock()
        mock_create_user.return_value = mock_user
        mock_generate_token_user.return_value = {"access_token": "fake_access_token",
                                                 "refresh_token": "fake_refresh_token"}

        response = register_user_with_source(
            create_user_request=create_user_request,
            registration_source=registration_source
        )
        assert response == {"access_token": "fake_access_token", "refresh_token": "fake_refresh_token"}


def test_register_user_with_google_success():
    create_user_request = CreateUserRequest(
        firstname="John",
        lastname="Doe",
        email="test@gmail.com",
        password="",
    )
    registration_source = RegistrationSource.GOOGLE
    with patch('pecha_api.auth.auth_service._create_user') as mock_create_user, \
            patch('pecha_api.auth.auth_service.generate_token_user') as mock_generate_token_user:
        mock_user = MagicMock()
        mock_create_user.return_value = mock_user
        mock_generate_token_user.return_value = {"access_token": "fake_access_token",
                                                 "refresh_token": "fake_refresh_token"}

        response = register_user_with_source(create_user_request, registration_source)

        mock_create_user.assert_called_once_with(create_user_request=create_user_request,
                                                 registration_source=registration_source)
        mock_generate_token_user.assert_called_once_with(mock_user)
        assert response == {"access_token": "fake_access_token", "refresh_token": "fake_refresh_token"}


def test_register_user_with_facebook_success():
    create_user_request = CreateUserRequest(
        firstname="John",
        lastname="Doe",
        email="test@gmail.com",
        password="",
    )
    registration_source = RegistrationSource.FACEBOOK
    with patch('pecha_api.auth.auth_service._create_user') as mock_create_user, \
            patch('pecha_api.auth.auth_service.generate_token_user') as mock_generate_token_user:
        mock_user = MagicMock()
        mock_create_user.return_value = mock_user
        mock_generate_token_user.return_value = {"access_token": "fake_access_token",
                                                 "refresh_token": "fake_refresh_token"}

        response = register_user_with_source(create_user_request, registration_source)

        mock_create_user.assert_called_once_with(create_user_request=create_user_request,
                                                 registration_source=registration_source)
        mock_generate_token_user.assert_called_once_with(mock_user)
        assert response == {"access_token": "fake_access_token", "refresh_token": "fake_refresh_token"}


def test_register_user_with_source_http_exception():
    create_user_request = CreateUserRequest(
        firstname="John",
        lastname="Doe",
        email="test@example.com",
        password="password123",
        username="testuser"
    )
    registration_source = RegistrationSource.EMAIL

    with patch('pecha_api.auth.auth_service._create_user') as mock_create_user:
        mock_create_user.side_effect = HTTPException(status_code=400, detail="User already exists")

        response = register_user_with_source(create_user_request, registration_source)
        print(f"response: {response}")

        assert response.status_code == 400
        error_message = json.loads(response.body)
        assert error_message == {"message": "User already exists"}


def test_generate_token_user_success():
    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    user.firstname = "John"
    user.lastname = "Doe"

    with patch('pecha_api.auth.auth_service.generate_token_data') as mock_generate_token_data, \
            patch('pecha_api.auth.auth_service.create_access_token') as mock_create_access_token, \
            patch('pecha_api.auth.auth_service.create_refresh_token') as mock_create_refresh_token:
        mock_generate_token_data.return_value = {"sub": user.email}
        mock_create_access_token.return_value = "fake_access_token"
        mock_create_refresh_token.return_value = "fake_refresh_token"

        response = generate_token_user(user)

        mock_generate_token_data.assert_called_once_with(user)
        mock_create_access_token.assert_called_once_with({"sub": user.email})
        mock_create_refresh_token.assert_called_once_with({"sub": user.email})
        assert response.user.name == "John Doe"
        assert response.user.avatar_url == ""
        assert response.auth.token_type == "Bearer"
        assert response.auth.access_token == "fake_access_token"
        assert response.auth.refresh_token == "fake_refresh_token"
        assert response.auth.token_type == "Bearer"


def test_generate_token_user_http_exception():
    user = MagicMock()
    user.id = uuid.UUID
    user.email = "test@example.com"
    user.username = "testuser"

    with patch('pecha_api.auth.auth_service.generate_token_data') as mock_generate_token_data:
        mock_generate_token_data.side_effect = HTTPException(status_code=500, detail="Internal Server Error")

        response = generate_token_user(user)

        mock_generate_token_data.assert_called_once_with(user)
        assert response.status_code == 500
        error_message = json.loads(response.body)
        assert error_message == {"message": "Internal Server Error"}


def test_authenticate_user_success():
    email = "test@example.com"
    password = "password123"
    user = MagicMock()
    user.email = email
    user.password = get_hashed_password(password)

    with patch('pecha_api.auth.auth_service.get_user_by_email') as mock_get_user_by_email, \
            patch('pecha_api.auth.auth_service.verify_password') as mock_verify_password:
        mock_get_user_by_email.return_value = user
        mock_verify_password.return_value = True

        authenticated_user = authenticate_user(email, password)

        mock_get_user_by_email.assert_called_once_with(db=ANY, email=email)
        mock_verify_password.assert_called_once_with(plain_password=password, hashed_password=user.password)
        assert authenticated_user == user


def test_authenticate_user_invalid_email():
    email = "invalid@example.com"
    password = "password123"

    with patch('pecha_api.auth.auth_service.get_user_by_email') as mock_get_user_by_email:
        mock_get_user_by_email.return_value = None

        try:
            authenticate_user(email, password)
        except HTTPException as e:
            assert e.status_code == status.HTTP_401_UNAUTHORIZED
            assert e.detail == 'Invalid email or password'

        mock_get_user_by_email.assert_called_once_with(db=ANY, email=email)


def test_authenticate_user_invalid_password():
    email = "test@example.com"
    password = "invalidpassword"
    user = MagicMock()
    user.email = email
    user.password = get_hashed_password("correctpassword")

    with patch('pecha_api.auth.auth_service.get_user_by_email') as mock_get_user_by_email, \
            patch('pecha_api.auth.auth_service.verify_password') as mock_verify_password:
        mock_get_user_by_email.return_value = user

        try:
            authenticate_user(email, password)
        except HTTPException as e:
            assert e.status_code == status.HTTP_401_UNAUTHORIZED
            assert e.detail == 'Invalid email or password'

    mock_get_user_by_email.assert_called_once_with(db=ANY, email=email)
    mock_verify_password.assert_called_once_with(plain_password=password, hashed_password=user.password)


def test_refresh_access_token_success():
    refresh_token = "valid_refresh_token"
    user = MagicMock()
    user.email = "test@example.com"
    user.firstname = "firstname"
    user.lastname = "lastname"

    with patch('pecha_api.auth.auth_service.decode_token') as mock_decode_token, \
            patch('pecha_api.auth.auth_service.get_user_by_email') as mock_get_user_by_email, \
            patch('pecha_api.auth.auth_service.generate_token_data') as mock_generate_token_data, \
            patch('pecha_api.auth.auth_service.create_access_token') as mock_create_access_token:
        mock_decode_token.return_value = {"sub": user.email}
        mock_get_user_by_email.return_value = user
        mock_generate_token_data.return_value = {"sub": user.email}
        mock_create_access_token.return_value = "new_access_token"

        response = refresh_access_token(refresh_token)

        mock_decode_token.assert_called_once_with(refresh_token)
        mock_get_user_by_email.assert_called_once_with(db=ANY, email=user.email)
        mock_generate_token_data.assert_called_once_with(user)
        assert response.access_token == "new_access_token"
        assert response.token_type == "Bearer"


def test_refresh_access_token_invalid_token():
    refresh_token = "invalid_refresh_token"

    with patch('pecha_api.auth.auth_service.decode_token') as mock_decode_token:
        mock_decode_token.side_effect = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                                      detail="Invalid refresh token")

        try:
            refresh_access_token(refresh_token)
        except HTTPException as e:
            assert e.status_code == status.HTTP_401_UNAUTHORIZED
            assert e.detail == "Invalid refresh token"

        mock_decode_token.assert_called_once_with(refresh_token)


def test_refresh_access_token_expired_token():
    refresh_token = "expired_refresh_token"

    with patch('pecha_api.auth.auth_service.decode_token') as mock_decode_token:
        mock_decode_token.side_effect = jwt.ExpiredSignatureError

        try:
            refresh_access_token(refresh_token)
        except HTTPException as e:
            assert e.status_code == status.HTTP_401_UNAUTHORIZED
            assert e.detail == "Refresh token expired"

        mock_decode_token.assert_called_once_with(refresh_token)


def test_refresh_access_token_user_not_found():
    refresh_token = "valid_refresh_token"

    with patch('pecha_api.auth.auth_service.decode_token') as mock_decode_token, \
            patch('pecha_api.auth.auth_service.get_user_by_email') as mock_get_user_by_email:
        mock_decode_token.return_value = {"sub": "test@example.com"}
        mock_get_user_by_email.return_value = None

        try:
            refresh_access_token(refresh_token)
        except HTTPException as e:
            assert e.status_code == status.HTTP_401_UNAUTHORIZED
            assert e.detail == "Invalid refresh token"

        mock_decode_token.assert_called_once_with(refresh_token)
        mock_get_user_by_email.assert_called_once_with(db=ANY, email="test@example.com")


def test_create_user_with_email_success():
    create_user_request = CreateUserRequest(
        firstname="John",
        lastname="Doe",
        email="test@example.com",
        password="password123"
    )
    registration_source = RegistrationSource.EMAIL

    with patch('pecha_api.auth.auth_service.save_user') as mock_save_user, \
            patch('pecha_api.auth.auth_service.get_hashed_password') as mock_get_hashed_password:
        mock_user = MagicMock()
        mock_save_user.return_value = mock_user
        mock_get_hashed_password.return_value = "hashed_password123"

        response = _create_user(create_user_request, registration_source)

        mock_get_hashed_password.assert_called_once_with("password123")
        mock_save_user.assert_called_once()
        assert response == mock_user


def test_create_user_with_google_success():
    create_user_request = CreateUserRequest(
        firstname="John",
        lastname="Doe",
        email="test@gmail.com",
        password=""
    )
    registration_source = RegistrationSource.GOOGLE

    with patch('pecha_api.auth.auth_service.save_user') as mock_save_user:
        mock_user = MagicMock()
        mock_save_user.return_value = mock_user

        response = _create_user(create_user_request, registration_source)

        mock_save_user.assert_called_once()
        assert response == mock_user


def test_create_user_with_facebook_success():
    create_user_request = CreateUserRequest(
        firstname="John",
        lastname="Doe",
        email="test@gmail.com",
        password=""
    )
    registration_source = RegistrationSource.FACEBOOK

    with patch('pecha_api.auth.auth_service.save_user') as mock_save_user:
        mock_user = MagicMock()
        mock_save_user.return_value = mock_user

        response = _create_user(create_user_request, registration_source)

        mock_save_user.assert_called_once()
        assert response == mock_user


def test_create_user_with_empty_password():
    create_user_request = CreateUserRequest(
        firstname="John",
        lastname="Doe",
        email="test@example.com",
        password=""
    )
    registration_source = RegistrationSource.EMAIL

    try:
        _create_user(create_user_request, registration_source)
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST
        assert e.detail == "Password cannot be empty"


def test_create_user_with_short_password():
    create_user_request = CreateUserRequest(
        firstname="John",
        lastname="Doe",
        email="test@example.com",
        password="short"
    )
    registration_source = RegistrationSource.EMAIL

    try:
        _create_user(create_user_request, registration_source)
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST
        assert e.detail == "Password must be between 8 and 20 characters"


def test_validate_user_already_exist_user_exists():
    email = "existing@example.com"

    with patch('pecha_api.auth.auth_service.get_user_by_email') as mock_get_user_by_email:
        mock_get_user_by_email.return_value = MagicMock()

        try:
            validate_user_already_exist(email)
        except HTTPException as e:
            assert e.status_code == status.HTTP_400_BAD_REQUEST
            assert e.detail == 'Email or username already exists'

        mock_get_user_by_email.assert_called_once_with(db=ANY, email=email)


def test_validate_user_already_exist_user_does_not_exist():
    email = "new@example.com"

    with patch('pecha_api.auth.auth_service.get_user_by_email') as mock_get_user_by_email:
        mock_get_user_by_email.return_value = None

        validate_user_already_exist(email)

        mock_get_user_by_email.assert_called_once_with(db=ANY, email=email)


def test_authenticate_and_generate_tokens_success():
    email = "test@example.com"
    password = "password123"
    user = MagicMock()
    user.email = email
    user.password = get_hashed_password(password)

    with patch('pecha_api.auth.auth_service.authenticate_user') as mock_authenticate_user, \
            patch('pecha_api.auth.auth_service.generate_token_user') as mock_generate_token_user:
        mock_authenticate_user.return_value = user
        mock_generate_token_user.return_value = {"access_token": "fake_access_token",
                                                 "refresh_token": "fake_refresh_token"}

        response = authenticate_and_generate_tokens(email, password)

        mock_authenticate_user.assert_called_once_with(email=email, password=password)
        mock_generate_token_user.assert_called_once_with(user)
        assert response == {"access_token": "fake_access_token", "refresh_token": "fake_refresh_token"}


def test_authenticate_and_generate_tokens_invalid_credentials():
    email = "invalid@example.com"
    password = "password123"

    with patch('pecha_api.auth.auth_service.authenticate_user') as mock_authenticate_user:
        mock_authenticate_user.side_effect = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                                           detail='Invalid email or password')

        response = authenticate_and_generate_tokens(email, password)

        mock_authenticate_user.assert_called_once_with(email=email, password=password)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_message = json.loads(response.body)
        assert error_message == {"message": "Invalid email or password"}


def test_authenticate_and_generate_tokens_internal_server_error():
    email = "test@example.com"
    password = "password123"
    user = MagicMock()
    user.email = email
    user.password = get_hashed_password(password)

    with patch('pecha_api.auth.auth_service.authenticate_user') as mock_authenticate_user, \
            patch('pecha_api.auth.auth_service.generate_token_user') as mock_generate_token_user:
        mock_authenticate_user.return_value = user
        mock_generate_token_user.side_effect = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                             detail='Internal Server Error')

        response = authenticate_and_generate_tokens(email, password)

        mock_authenticate_user.assert_called_once_with(email=email, password=password)
        mock_generate_token_user.assert_called_once_with(user)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        error_message = json.loads(response.body)
        assert error_message == {"message": "Internal Server Error"}
