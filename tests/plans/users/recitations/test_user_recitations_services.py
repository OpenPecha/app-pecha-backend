import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from fastapi import HTTPException
from starlette import status

from pecha_api.plans.users.recitation.user_recitations_services import create_user_recitation_service
from pecha_api.plans.users.recitation.user_recitations_response_models import CreateUserRecitationRequest
from pecha_api.plans.users.recitation.user_recitations_models import UserRecitations
from pecha_api.users.users_models import Users
from pecha_api.error_contants import ErrorConstants


class TestDataFactory:
    """Factory class for creating test data objects."""
    
    @staticmethod
    def create_mock_user(
        user_id=None,
        email="test@example.com",
        username="testuser"
    ) -> MagicMock:
        """Create a mock User object with specified attributes."""
        mock_user = MagicMock(spec=Users)
        mock_user.id = user_id or uuid4()
        mock_user.email = email
        mock_user.username = username
        return mock_user

    @staticmethod
    def create_user_recitation_request(text_id=None) -> CreateUserRecitationRequest:
        """Create a CreateUserRecitationRequest with specified text_id."""
        return CreateUserRecitationRequest(
            text_id=text_id or uuid4()
        )


class TestCreateUserRecitationService:
    """Test cases for create_user_recitation_service function."""

    @patch('pecha_api.plans.users.recitation.user_recitations_services.save_user_recitation')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.SessionLocal')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.TextUtils.validate_text_exists')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.validate_and_extract_user_details')
    @pytest.mark.asyncio
    async def test_create_user_recitation_service_success(
        self,
        mock_validate_user,
        mock_validate_text,
        mock_session_local,
        mock_save_user_recitation
    ):
        """Test successful creation of user recitation."""
        user_id = uuid4()
        text_id = uuid4()
        token = "valid_token"
        
        mock_user = TestDataFactory.create_mock_user(user_id=user_id)
        mock_validate_user.return_value = mock_user
        mock_validate_text.return_value = True
        
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        
        request = TestDataFactory.create_user_recitation_request(text_id=text_id)
        
        result = await create_user_recitation_service(
            token=token,
            create_user_recitation_request=request
        )
        
        assert result is None
        mock_validate_user.assert_called_once_with(token=token)
        mock_validate_text.assert_awaited_once_with(text_id=str(text_id))
        mock_save_user_recitation.assert_called_once()
        
        call_args = mock_save_user_recitation.call_args
        assert call_args[1]['db'] == mock_db
        user_recitation = call_args[1]['user_recitations']
        assert isinstance(user_recitation, UserRecitations)
        assert user_recitation.user_id == user_id
        assert user_recitation.text_id == text_id

    @patch('pecha_api.plans.users.recitation.user_recitations_services.TextUtils.validate_text_exists')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.validate_and_extract_user_details')
    @pytest.mark.asyncio
    async def test_create_user_recitation_service_text_not_found(
        self,
        mock_validate_user,
        mock_validate_text
    ):
        """Test create_user_recitation_service when text does not exist."""
        user_id = uuid4()
        text_id = uuid4()
        token = "valid_token"
        
        mock_user = TestDataFactory.create_mock_user(user_id=user_id)
        mock_validate_user.return_value = mock_user
        
        mock_validate_text.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE
        )
        
        request = TestDataFactory.create_user_recitation_request(text_id=text_id)
        
        with pytest.raises(HTTPException) as exc_info:
            await create_user_recitation_service(
                token=token,
                create_user_recitation_request=request
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE
        mock_validate_user.assert_called_once_with(token=token)
        mock_validate_text.assert_awaited_once_with(text_id=str(text_id))