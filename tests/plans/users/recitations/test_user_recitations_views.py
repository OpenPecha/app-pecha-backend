import pytest
from unittest.mock import patch
from uuid import uuid4
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette import status

from pecha_api.plans.users.recitation.user_recitations_views import create_user_recitation, get_user_recitations
from pecha_api.plans.users.recitation.user_recitations_response_models import (
    CreateUserRecitationRequest,
    UserRecitationsResponse,
    UserRecitationDTO
)

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

    @staticmethod
    def create_user_recitations_response(recitations=None) -> UserRecitationsResponse:
        """Create a UserRecitationsResponse with specified recitations."""
        return UserRecitationsResponse(
            recitations=recitations or []
        )

    @staticmethod
    def create_user_recitation_dto(title="Test Text", text_id=None) -> UserRecitationDTO:
        """Create a UserRecitationDTO with specified attributes."""
        return UserRecitationDTO(
            title=title,
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

class TestGetUserRecitationsView:
    """Test cases for get_user_recitations view function."""

    @patch('pecha_api.plans.users.recitation.user_recitations_views.get_user_recitations_service')
    @pytest.mark.asyncio
    async def test_get_user_recitations_success(
        self,
        mock_service
    ):
        """Test successful retrieval of user recitations with multiple texts."""
        token = "valid_token"
        text_id_1 = uuid4()
        text_id_2 = uuid4()
        
        auth_credentials = TestDataFactory.create_auth_credentials(token=token)
        
        recitations = [
            TestDataFactory.create_user_recitation_dto(
                title="Heart Sutra",
                text_id=text_id_1
            ),
            TestDataFactory.create_user_recitation_dto(
                title="Diamond Sutra",
                text_id=text_id_2
            )
        ]
        mock_response = TestDataFactory.create_user_recitations_response(recitations=recitations)
        mock_service.return_value = mock_response
        
        result = await get_user_recitations(authentication_credential=auth_credentials)
        
        assert isinstance(result, UserRecitationsResponse)
        assert len(result.recitations) == 2
        assert result.recitations[0].title == "Heart Sutra"
        assert result.recitations[0].text_id == text_id_1
        assert result.recitations[1].title == "Diamond Sutra"
        assert result.recitations[1].text_id == text_id_2
        
        mock_service.assert_awaited_once_with(token=token)

    @patch('pecha_api.plans.users.recitation.user_recitations_views.get_user_recitations_service')
    @pytest.mark.asyncio
    async def test_get_user_recitations_empty_list(
        self,
        mock_service
    ):
        """Test retrieval when user has no recitations."""
        token = "valid_token"
        
        auth_credentials = TestDataFactory.create_auth_credentials(token=token)
        
        mock_response = TestDataFactory.create_user_recitations_response(recitations=[])
        mock_service.return_value = mock_response
        
        result = await get_user_recitations(authentication_credential=auth_credentials)
        
        assert isinstance(result, UserRecitationsResponse)
        assert len(result.recitations) == 0
        assert result.recitations == []
        
        mock_service.assert_awaited_once_with(token=token)

    @patch('pecha_api.plans.users.recitation.user_recitations_views.get_user_recitations_service')
    @pytest.mark.asyncio
    async def test_get_user_recitations_single_recitation(
        self,
        mock_service
    ):
        """Test retrieval when user has a single recitation."""
        token = "valid_token"
        text_id = uuid4()
        
        auth_credentials = TestDataFactory.create_auth_credentials(token=token)
        
        recitations = [
            TestDataFactory.create_user_recitation_dto(
                title="Lotus Sutra",
                text_id=text_id
            )
        ]
        mock_response = TestDataFactory.create_user_recitations_response(recitations=recitations)
        mock_service.return_value = mock_response
        
        result = await get_user_recitations(authentication_credential=auth_credentials)
        
        assert isinstance(result, UserRecitationsResponse)
        assert len(result.recitations) == 1
        assert result.recitations[0].title == "Lotus Sutra"
        assert result.recitations[0].text_id == text_id
        
        mock_service.assert_awaited_once_with(token=token)

    @patch('pecha_api.plans.users.recitation.user_recitations_views.get_user_recitations_service')
    @pytest.mark.asyncio
    async def test_get_user_recitations_invalid_token(
        self,
        mock_service
    ):
        """Test get_user_recitations with invalid authentication token."""
        token = "invalid_token"
        
        auth_credentials = TestDataFactory.create_auth_credentials(token=token)
        
        mock_service.side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_user_recitations(authentication_credential=auth_credentials)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid authentication credentials"
        
        mock_service.assert_awaited_once_with(token=token)

    @patch('pecha_api.plans.users.recitation.user_recitations_views.get_user_recitations_service')
    @pytest.mark.asyncio
    async def test_get_user_recitations_database_error(
        self,
        mock_service
    ):
        """Test get_user_recitations when database error occurs."""
        token = "valid_token"
        
        auth_credentials = TestDataFactory.create_auth_credentials(token=token)
        
        mock_service.side_effect = HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_user_recitations(authentication_credential=auth_credentials)
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Database connection error"
        
        mock_service.assert_awaited_once_with(token=token)
