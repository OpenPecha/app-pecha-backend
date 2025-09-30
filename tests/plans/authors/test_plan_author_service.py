import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from jose import JWTError
from jose.exceptions import JWTClaimsError
from jwt import ExpiredSignatureError
from starlette import status

from pecha_api.plans.authors.plan_authors_service import validate_and_extract_author_details
from pecha_api.plans.authors.plan_authors_model import Author
from pecha_api.error_contants import ErrorConstants
import jose


class TestValidateAndExtractAuthorDetails:
    """Test cases for validate_and_extract_author_details function."""

    @patch('pecha_api.plans.authors.plan_author_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_author_service.get_author_by_email')
    @patch('pecha_api.plans.authors.plan_author_service.validate_token')
    def test_validate_and_extract_author_details_success(
        self, 
        mock_validate_token, 
        mock_get_author_by_email, 
        mock_session_local
    ):
        """Test successful token validation and author extraction."""
        # Arrange
        token = "valid_token"
        expected_payload = {"email": "test@example.com"}
        expected_author = MagicMock(spec=Author)
        mock_db_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db_session
        mock_validate_token.return_value = expected_payload
        mock_get_author_by_email.return_value = expected_author

        # Act
        result = validate_and_extract_author_details(token)

        # Assert
        assert result == expected_author
        mock_validate_token.assert_called_once_with(token)
        mock_get_author_by_email.assert_called_once_with(db=mock_db_session, email="test@example.com")

    @patch('pecha_api.plans.authors.plan_author_service.validate_token')
    def test_validate_and_extract_author_details_missing_email(
        self, 
        mock_validate_token
    ):
        """Test token validation when email is missing from payload."""
        # Arrange
        token = "token_without_email"
        mock_validate_token.return_value = {"name": "test_user"}  # No email field

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_author_service.validate_token')
    def test_validate_and_extract_author_details_none_email(
        self, 
        mock_validate_token
    ):
        """Test token validation when email is None in payload."""
        # Arrange
        token = "token_with_none_email"
        mock_validate_token.return_value = {"email": None}

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_author_service.validate_token')
    def test_validate_and_extract_author_details_expired_signature_error(
        self, 
        mock_validate_token
    ):
        """Test handling of ExpiredSignatureError from jwt library."""
        # Arrange
        token = "expired_token"
        mock_validate_token.side_effect = ExpiredSignatureError("Token has expired")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_author_service.validate_token')
    def test_validate_and_extract_author_details_jose_expired_signature_error(
        self, 
        mock_validate_token
    ):
        """Test handling of jose.ExpiredSignatureError."""
        # Arrange
        token = "expired_token"
        mock_validate_token.side_effect = jose.ExpiredSignatureError("Token has expired")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_author_service.validate_token')
    def test_validate_and_extract_author_details_jwt_claims_error(
        self, 
        mock_validate_token
    ):
        """Test handling of JWTClaimsError."""
        # Arrange
        token = "invalid_claims_token"
        mock_validate_token.side_effect = JWTClaimsError("Invalid claims")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_author_service.validate_token')
    def test_validate_and_extract_author_details_value_error(
        self, 
        mock_validate_token
    ):
        """Test handling of ValueError."""
        # Arrange
        token = "invalid_token"
        mock_validate_token.side_effect = ValueError("Invalid token format")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_author_service.validate_token')
    def test_validate_and_extract_author_details_jwt_error(
        self, 
        mock_validate_token
    ):
        """Test handling of JWTError."""
        # Arrange
        token = "jwt_error_token"
        mock_validate_token.side_effect = JWTError("JWT error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == ErrorConstants.TOKEN_ERROR_MESSAGE

    @patch('pecha_api.plans.authors.plan_author_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_author_service.get_author_by_email')
    @patch('pecha_api.plans.authors.plan_author_service.validate_token')
    def test_validate_and_extract_author_details_database_error(
        self, 
        mock_validate_token, 
        mock_get_author_by_email, 
        mock_session_local
    ):
        """Test handling of database session error."""
        # Arrange
        token = "valid_token"
        expected_payload = {"email": "test@example.com"}
        mock_validate_token.return_value = expected_payload
        mock_session_local.side_effect = Exception("Database connection error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            validate_and_extract_author_details(token)

        assert str(exc_info.value) == "Database connection error"

    @patch('pecha_api.plans.authors.plan_author_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_author_service.get_author_by_email')
    @patch('pecha_api.plans.authors.plan_author_service.validate_token')
    def test_validate_and_extract_author_details_author_not_found(
        self, 
        mock_validate_token, 
        mock_get_author_by_email, 
        mock_session_local
    ):
        """Test handling when author is not found in database."""
        # Arrange
        token = "valid_token"
        expected_payload = {"email": "nonexistent@example.com"}
        mock_db_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db_session
        mock_validate_token.return_value = expected_payload
        mock_get_author_by_email.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_extract_author_details(token)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "User not found"

    @patch('pecha_api.plans.authors.plan_author_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_author_service.get_author_by_email')
    @patch('pecha_api.plans.authors.plan_author_service.validate_token')
    def test_validate_and_extract_author_details_logging_debug_called(
        self, 
        mock_validate_token, 
        mock_get_author_by_email, 
        mock_session_local
    ):
        """Test that logging.debug is called for exceptions."""
        # Arrange
        token = "invalid_token"
        mock_validate_token.side_effect = ValueError("Invalid token format")

        # Act & Assert
        with patch('pecha_api.plans.authors.plan_author_service.logging.debug') as mock_logging:
            with pytest.raises(HTTPException):
                validate_and_extract_author_details(token)
            
            mock_logging.assert_called_once_with("exception: Invalid token format")

    @patch('pecha_api.plans.authors.plan_author_service.SessionLocal')
    @patch('pecha_api.plans.authors.plan_author_service.get_author_by_email')
    @patch('pecha_api.plans.authors.plan_author_service.validate_token')
    def test_validate_and_extract_author_details_database_session_context_manager(
        self, 
        mock_validate_token, 
        mock_get_author_by_email, 
        mock_session_local
    ):
        """Test that database session is properly used as context manager."""
        # Arrange
        token = "valid_token"
        expected_payload = {"email": "test@example.com"}
        expected_author = MagicMock(spec=Author)
        mock_db_session = MagicMock()
        mock_session_context = MagicMock()
        mock_session_context.__enter__.return_value = mock_db_session
        mock_session_local.return_value = mock_session_context
        mock_validate_token.return_value = expected_payload
        mock_get_author_by_email.return_value = expected_author

        # Act
        result = validate_and_extract_author_details(token)

        # Assert
        assert result == expected_author
        mock_session_local.assert_called_once()
        mock_session_context.__enter__.assert_called_once()
        mock_session_context.__exit__.assert_called_once()
        mock_get_author_by_email.assert_called_once_with(db=mock_db_session, email="test@example.com")
