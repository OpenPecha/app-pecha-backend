import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from fastapi import HTTPException
from starlette import status

from pecha_api.plans.users.recitation.user_recitations_services import (
    create_user_recitation_service,
    get_user_recitations_service,
    delete_user_recitation_service
)
from pecha_api.plans.users.recitation.user_recitations_response_models import (
    CreateUserRecitationRequest,
    UserRecitationsResponse,
    UserRecitationDTO
)
from pecha_api.plans.users.recitation.user_recitations_models import UserRecitations
from pecha_api.users.users_models import Users
from pecha_api.error_contants import ErrorConstants


class TestDataFactory:    
    @staticmethod
    def create_mock_user(
        user_id=None,
        email="test@example.com",
        username="testuser"
    ) -> MagicMock:
        mock_user = MagicMock(spec=Users)
        mock_user.id = user_id or uuid4()
        mock_user.email = email
        mock_user.username = username
        return mock_user

    @staticmethod
    def create_user_recitation_request(text_id=None) -> CreateUserRecitationRequest:
        return CreateUserRecitationRequest(
            text_id=text_id or uuid4()
        )
      
    @staticmethod
    def create_mock_user_recitation(user_id=None, text_id=None) -> MagicMock:
        mock_recitation = MagicMock(spec=UserRecitations)
        mock_recitation.user_id = user_id or uuid4()
        mock_recitation.text_id = text_id or uuid4()
        return mock_recitation


class TestCreateUserRecitationService:
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


class TestGetUserRecitationsService:
    @patch('pecha_api.plans.users.recitation.user_recitations_services.get_texts_by_ids')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.get_user_recitations_by_user_id')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.SessionLocal')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.validate_and_extract_user_details')
    @pytest.mark.asyncio
    async def test_get_user_recitations_service_success(
        self,
        mock_validate_user,
        mock_session_local,
        mock_get_recitations,
        mock_get_texts
    ):
        user_id = uuid4()
        text_id_1 = uuid4()
        text_id_2 = uuid4()
        token = "valid_token"
        
        mock_user = TestDataFactory.create_mock_user(user_id=user_id)
        mock_validate_user.return_value = mock_user
        
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        
        mock_recitation_1 = TestDataFactory.create_mock_user_recitation(
            user_id=user_id,
            text_id=text_id_1
        )
        mock_recitation_2 = TestDataFactory.create_mock_user_recitation(
            user_id=user_id,
            text_id=text_id_2
        )
        mock_get_recitations.return_value = [mock_recitation_1, mock_recitation_2]
        
        mock_text_1 = MagicMock()
        mock_text_1.title = "Heart Sutra"
        mock_text_2 = MagicMock()
        mock_text_2.title = "Diamond Sutra"
        
        mock_get_texts.return_value = {
            str(text_id_1): mock_text_1,
            str(text_id_2): mock_text_2
        }
        
        result = await get_user_recitations_service(token=token)
        
        assert isinstance(result, UserRecitationsResponse)
        assert len(result.recitations) == 2
        assert result.recitations[0].title == "Heart Sutra"
        assert result.recitations[0].text_id == text_id_1
        assert result.recitations[1].title == "Diamond Sutra"
        assert result.recitations[1].text_id == text_id_2
        
        mock_validate_user.assert_called_once_with(token=token)
        mock_get_recitations.assert_called_once_with(db=mock_db, user_id=user_id)
        mock_get_texts.assert_awaited_once_with(text_ids=[str(text_id_1), str(text_id_2)])

    @patch('pecha_api.plans.users.recitation.user_recitations_services.get_user_recitations_by_user_id')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.SessionLocal')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.validate_and_extract_user_details')
    @pytest.mark.asyncio
    async def test_get_user_recitations_service_empty_list(
        self,
        mock_validate_user,
        mock_session_local,
        mock_get_recitations
    ):
        user_id = uuid4()
        token = "valid_token"
        
        mock_user = TestDataFactory.create_mock_user(user_id=user_id)
        mock_validate_user.return_value = mock_user
        
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        
        mock_get_recitations.return_value = []
        
        result = await get_user_recitations_service(token=token)
        
        assert isinstance(result, UserRecitationsResponse)
        assert len(result.recitations) == 0
        assert result.recitations == []
        
        mock_validate_user.assert_called_once_with(token=token)
        mock_get_recitations.assert_called_once_with(db=mock_db, user_id=user_id)

    @patch('pecha_api.plans.users.recitation.user_recitations_services.get_texts_by_ids')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.get_user_recitations_by_user_id')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.SessionLocal')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.validate_and_extract_user_details')
    @pytest.mark.asyncio
    async def test_get_user_recitations_service_single_recitation(
        self,
        mock_validate_user,
        mock_session_local,
        mock_get_recitations,
        mock_get_texts
    ):
        user_id = uuid4()
        text_id = uuid4()
        token = "valid_token"
        
        mock_user = TestDataFactory.create_mock_user(user_id=user_id)
        mock_validate_user.return_value = mock_user
        
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        
        mock_recitation = TestDataFactory.create_mock_user_recitation(
            user_id=user_id,
            text_id=text_id
        )
        mock_get_recitations.return_value = [mock_recitation]
        
        mock_text = MagicMock()
        mock_text.title = "Lotus Sutra"
        mock_get_texts.return_value = {str(text_id): mock_text}
        
        result = await get_user_recitations_service(token=token)
        
        assert isinstance(result, UserRecitationsResponse)
        assert len(result.recitations) == 1
        assert result.recitations[0].title == "Lotus Sutra"
        assert result.recitations[0].text_id == text_id
        
        mock_validate_user.assert_called_once_with(token=token)
        mock_get_recitations.assert_called_once_with(db=mock_db, user_id=user_id)
        mock_get_texts.assert_awaited_once_with(text_ids=[str(text_id)])

    @patch('pecha_api.plans.users.recitation.user_recitations_services.get_texts_by_ids')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.get_user_recitations_by_user_id')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.SessionLocal')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.validate_and_extract_user_details')
    @pytest.mark.asyncio
    async def test_get_user_recitations_service_text_not_found_in_mongodb(
        self,
        mock_validate_user,
        mock_session_local,
        mock_get_recitations,
        mock_get_texts
    ):
        user_id = uuid4()
        text_id_1 = uuid4()
        text_id_2 = uuid4()
        text_id_3 = uuid4()
        token = "valid_token"
        
        mock_user = TestDataFactory.create_mock_user(user_id=user_id)
        mock_validate_user.return_value = mock_user
        
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        
        mock_recitation_1 = TestDataFactory.create_mock_user_recitation(
            user_id=user_id,
            text_id=text_id_1
        )
        mock_recitation_2 = TestDataFactory.create_mock_user_recitation(
            user_id=user_id,
            text_id=text_id_2
        )
        mock_recitation_3 = TestDataFactory.create_mock_user_recitation(
            user_id=user_id,
            text_id=text_id_3
        )
        mock_get_recitations.return_value = [
            mock_recitation_1,
            mock_recitation_2,
            mock_recitation_3
        ]
        
        mock_text_1 = MagicMock()
        mock_text_1.title = "Heart Sutra"
        mock_text_3 = MagicMock()
        mock_text_3.title = "Lotus Sutra"
        
        mock_get_texts.return_value = {
            str(text_id_1): mock_text_1,
            str(text_id_3): mock_text_3
        }
        
        result = await get_user_recitations_service(token=token)
        
        assert isinstance(result, UserRecitationsResponse)
        assert len(result.recitations) == 2
        assert result.recitations[0].title == "Heart Sutra"
        assert result.recitations[0].text_id == text_id_1
        assert result.recitations[1].title == "Lotus Sutra"
        assert result.recitations[1].text_id == text_id_3
        
        mock_validate_user.assert_called_once_with(token=token)
        mock_get_recitations.assert_called_once_with(db=mock_db, user_id=user_id)
        mock_get_texts.assert_awaited_once_with(
            text_ids=[str(text_id_1), str(text_id_2), str(text_id_3)]
        )

    @patch('pecha_api.plans.users.recitation.user_recitations_services.SessionLocal')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.validate_and_extract_user_details')
    @pytest.mark.asyncio
    async def test_get_user_recitations_service_invalid_token(
        self,
        mock_validate_user,
        mock_session_local
    ):
        token = "invalid_token"
        
        mock_validate_user.side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_user_recitations_service(token=token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid authentication credentials"
        
        mock_validate_user.assert_called_once_with(token=token)

    @patch('pecha_api.plans.users.recitation.user_recitations_services.get_user_recitations_by_user_id')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.SessionLocal')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.validate_and_extract_user_details')
    @pytest.mark.asyncio
    async def test_get_user_recitations_service_database_error(
        self,
        mock_validate_user,
        mock_session_local,
        mock_get_recitations
    ):
        user_id = uuid4()
        token = "valid_token"
        
        mock_user = TestDataFactory.create_mock_user(user_id=user_id)
        mock_validate_user.return_value = mock_user
        
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        
        mock_get_recitations.side_effect = Exception("Database connection error")
        
        with pytest.raises(Exception) as exc_info:
            await get_user_recitations_service(token=token)
        
        assert str(exc_info.value) == "Database connection error"
        
        mock_validate_user.assert_called_once_with(token=token)
        mock_get_recitations.assert_called_once_with(db=mock_db, user_id=user_id)

    @patch('pecha_api.plans.users.recitation.user_recitations_services.get_texts_by_ids')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.get_user_recitations_by_user_id')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.SessionLocal')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.validate_and_extract_user_details')
    @pytest.mark.asyncio
    async def test_get_user_recitations_service_mongodb_error(
        self,
        mock_validate_user,
        mock_session_local,
        mock_get_recitations,
        mock_get_texts
    ):
        user_id = uuid4()
        text_id = uuid4()
        token = "valid_token"
        
        mock_user = TestDataFactory.create_mock_user(user_id=user_id)
        mock_validate_user.return_value = mock_user

        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        
        mock_recitation = TestDataFactory.create_mock_user_recitation(
            user_id=user_id,
            text_id=text_id
        )
        mock_get_recitations.return_value = [mock_recitation]
        
        mock_get_texts.side_effect = Exception("MongoDB connection error")
        
        with pytest.raises(Exception) as exc_info:
            await get_user_recitations_service(token=token)
        
        assert str(exc_info.value) == "MongoDB connection error"
        
        mock_validate_user.assert_called_once_with(token=token)


class TestDeleteUserRecitationService:

    @patch('pecha_api.plans.users.recitation.user_recitations_services.delete_user_recitation')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.SessionLocal')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.validate_and_extract_user_details')
    @pytest.mark.asyncio
    async def test_delete_user_recitation_service_success(
        self,
        mock_validate_user,
        mock_session_local,
        mock_delete_recitation
    ):
        """Test successful deletion of user recitation."""
        user_id = uuid4()
        text_id = uuid4()
        token = "valid_token"
        
        mock_user = TestDataFactory.create_mock_user(user_id=user_id)
        mock_validate_user.return_value = mock_user
        
        mock_db_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db_session
        mock_session_local.return_value.__exit__.return_value = None
        
        mock_delete_recitation.return_value = None
        
        result = await delete_user_recitation_service(token=token, text_id=text_id)
        
        assert result is None
        mock_validate_user.assert_called_once_with(token=token)
        mock_delete_recitation.assert_called_once_with(
            db=mock_db_session,
            user_id=user_id,
            text_id=text_id
        )

    @patch('pecha_api.plans.users.recitation.user_recitations_services.delete_user_recitation')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.SessionLocal')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.validate_and_extract_user_details')
    @pytest.mark.asyncio
    async def test_delete_user_recitation_service_not_found(
        self,
        mock_validate_user,
        mock_session_local,
        mock_delete_recitation
    ):
        """Test delete_user_recitation_service when recitation does not exist."""
        user_id = uuid4()
        text_id = uuid4()
        token = "valid_token"
        
        mock_user = TestDataFactory.create_mock_user(user_id=user_id)
        mock_validate_user.return_value = mock_user
        
        mock_db_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db_session
        mock_session_local.return_value.__exit__.return_value = None
        
        mock_delete_recitation.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NOT_FOUND",
                "message": f"Recitation with ID {text_id} not found for this user"
            }
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await delete_user_recitation_service(token=token, text_id=text_id)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail["error"] == "NOT_FOUND"
        mock_validate_user.assert_called_once_with(token=token)
        mock_delete_recitation.assert_called_once_with(
            db=mock_db_session,
            user_id=user_id,
            text_id=text_id
        )

    @patch('pecha_api.plans.users.recitation.user_recitations_services.SessionLocal')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.validate_and_extract_user_details')
    @pytest.mark.asyncio
    async def test_delete_user_recitation_service_invalid_token(
        self,
        mock_validate_user,
        mock_session_local
    ):
        """Test delete_user_recitation_service with invalid authentication token."""
        text_id = uuid4()
        token = "invalid_token"
        
        mock_validate_user.side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await delete_user_recitation_service(token=token, text_id=text_id)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid authentication credentials"
        mock_validate_user.assert_called_once_with(token=token)
        mock_session_local.assert_not_called()

    @patch('pecha_api.plans.users.recitation.user_recitations_services.delete_user_recitation')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.SessionLocal')
    @patch('pecha_api.plans.users.recitation.user_recitations_services.validate_and_extract_user_details')
    @pytest.mark.asyncio
    async def test_delete_user_recitation_service_database_error(
        self,
        mock_validate_user,
        mock_session_local,
        mock_delete_recitation
    ):
        """Test delete_user_recitation_service when database error occurs."""
        user_id = uuid4()
        text_id = uuid4()
        token = "valid_token"
        
        mock_user = TestDataFactory.create_mock_user(user_id=user_id)
        mock_validate_user.return_value = mock_user
        
        mock_db_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db_session
        mock_session_local.return_value.__exit__.return_value = None
        
        mock_delete_recitation.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "BAD_REQUEST",
                "message": "Database integrity error: constraint violation"
            }
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await delete_user_recitation_service(token=token, text_id=text_id)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail["error"] == "BAD_REQUEST"
        mock_validate_user.assert_called_once_with(token=token)
        mock_delete_recitation.assert_called_once_with(
            db=mock_db_session,
            user_id=user_id,
            text_id=text_id
        )
