import pytest
from unittest.mock import patch
from uuid import uuid4
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette import status

from pecha_api.plans.users.recitation.user_recitations_views import create_user_recitation
from pecha_api.plans.users.recitation.user_recitations_response_models import CreateUserRecitationRequest
from pecha_api.error_contants import ErrorConstants


class TestDataFactory:
    """Factory class for creating test data objects."""
    
    @staticmethod
    def create_auth_credentials(token="valid_token") -> HTTPAuthorizationCredentials:
        """Create HTTPAuthorizationCredentials with specified token."""
        return HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

    @staticmethod
    def create_user_recitation_request(text_id=None) -> CreateUserRecitationRequest:
        """Create a CreateUserRecitationRequest with specified text_id."""
        return CreateUserRecitationRequest(
            text_id=text_id or uuid4()
        )


class TestCreateUserRecitationView:
    """Test cases for create_user_recitation view function."""

    @patch('pecha_api.plans.users.recitation.user_recitations_views.create_user_recitation_service')
    @pytest.mark.asyncio
    async def test_create_user_recitation_success(
        self,
        mock_service
    ):
        """Test successful creation of user recitation via view."""
        text_id = uuid4()
        token = "valid_token"
        
        auth_credentials = TestDataFactory.create_auth_credentials(token=token)
        request = TestDataFactory.create_user_recitation_request(text_id=text_id)
        
        mock_service.return_value = None
        
        result = await create_user_recitation(
            authentication_credential=auth_credentials,
            create_user_recitation_request=request
        )
        
        assert result is None
        mock_service.assert_awaited_once_with(
            token=token,
            create_user_recitation_request=request
        )

    @patch('pecha_api.plans.users.recitation.user_recitations_views.create_user_recitation_service')
    @pytest.mark.asyncio
    async def test_create_user_recitation_text_not_found(
        self,
        mock_service
    ):
        """Test create_user_recitation when text does not exist."""
        text_id = uuid4()
        token = "valid_token"
        
        auth_credentials = TestDataFactory.create_auth_credentials(token=token)
        request = TestDataFactory.create_user_recitation_request(text_id=text_id)
        
        mock_service.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await create_user_recitation(
                authentication_credential=auth_credentials,
                create_user_recitation_request=request
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE
        mock_service.assert_awaited_once_with(
            token=token,
            create_user_recitation_request=request
        )