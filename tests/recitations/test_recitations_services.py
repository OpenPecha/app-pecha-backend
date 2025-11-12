import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from pecha_api.recitations.recitations_services import get_list_of_recitations_service
from pecha_api.recitations.recitations_response_models import RecitationDTO, RecitationsResponse
from pecha_api.texts.texts_enums import TextType
from pecha_api.texts.texts_models import Text


class TestDataFactory:
    """Factory class for creating test data objects."""
    
    @staticmethod
    def create_mock_text(
        text_id=None,
        title="Sample Recitation",
        text_type=TextType.RECITATION
    ) -> MagicMock:
        """Create a mock Text object with specified attributes."""
        mock_text = MagicMock(spec=Text)
        mock_text.id = text_id or uuid4()
        mock_text.title = title
        mock_text.type = text_type
        return mock_text


class TestGetListOfRecitationsService:
    """Test cases for get_list_of_recitations_service function."""

    @patch('pecha_api.recitations.recitations_services.Text.get_list_of_recitations')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_success(
        self,
        mock_get_list_of_recitations
    ):
        """Test successful retrieval of recitations list."""
        text_id_1 = uuid4()
        text_id_2 = uuid4()
        
        mock_recitations = [
            TestDataFactory.create_mock_text(
                text_id=text_id_1,
                title="First Recitation"
            ),
            TestDataFactory.create_mock_text(
                text_id=text_id_2,
                title="Second Recitation"
            )
        ]
        
        mock_get_list_of_recitations.return_value = mock_recitations
        
        result = await get_list_of_recitations_service()
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 2
        
        first_recitation = result.recitations[0]
        assert isinstance(first_recitation, RecitationDTO)
        assert first_recitation.title == "First Recitation"
        assert first_recitation.text_id == text_id_1
        
        second_recitation = result.recitations[1]
        assert isinstance(second_recitation, RecitationDTO)
        assert second_recitation.title == "Second Recitation"
        assert second_recitation.text_id == text_id_2
        
        mock_get_list_of_recitations.assert_called_once_with(type=TextType.RECITATION)

    @patch('pecha_api.recitations.recitations_services.Text.get_list_of_recitations')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_empty_list(
        self,
        mock_get_list_of_recitations
    ):
        """Test get_list_of_recitations_service when no recitations exist."""
        mock_get_list_of_recitations.return_value = []
        
        result = await get_list_of_recitations_service()
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 0
        assert result.recitations == []
        
        mock_get_list_of_recitations.assert_called_once_with(type=TextType.RECITATION)

    @patch('pecha_api.recitations.recitations_services.Text.get_list_of_recitations')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_single_recitation(
        self,
        mock_get_list_of_recitations
    ):
        """Test get_list_of_recitations_service with single recitation."""
        text_id = uuid4()
        mock_recitation = TestDataFactory.create_mock_text(
            text_id=text_id,
            title="Single Recitation"
        )
        
        mock_get_list_of_recitations.return_value = [mock_recitation]
        
        result = await get_list_of_recitations_service()
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 1
        
        recitation = result.recitations[0]
        assert isinstance(recitation, RecitationDTO)
        assert recitation.title == "Single Recitation"
        assert recitation.text_id == text_id
        
        mock_get_list_of_recitations.assert_called_once_with(type=TextType.RECITATION)

    @patch('pecha_api.recitations.recitations_services.Text.get_list_of_recitations')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_multiple_recitations(
        self,
        mock_get_list_of_recitations
    ):
        """Test get_list_of_recitations_service with multiple recitations."""
        mock_recitations = []
        expected_titles = []
        expected_ids = []
        
        for i in range(5):
            text_id = uuid4()
            title = f"Recitation {i + 1}"
            mock_recitation = TestDataFactory.create_mock_text(
                text_id=text_id,
                title=title
            )
            mock_recitations.append(mock_recitation)
            expected_titles.append(title)
            expected_ids.append(text_id)
        
        mock_get_list_of_recitations.return_value = mock_recitations
        
        result = await get_list_of_recitations_service()
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 5
        
        for i, recitation in enumerate(result.recitations):
            assert isinstance(recitation, RecitationDTO)
            assert recitation.title == expected_titles[i]
            assert recitation.text_id == expected_ids[i]
        
        mock_get_list_of_recitations.assert_called_once_with(type=TextType.RECITATION)

    @patch('pecha_api.recitations.recitations_services.Text.get_list_of_recitations')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_database_error(
        self,
        mock_get_list_of_recitations
    ):
        """Test get_list_of_recitations_service when database operation fails."""
        mock_get_list_of_recitations.side_effect = Exception("Database connection error")
        
        with pytest.raises(Exception) as exc_info:
            await get_list_of_recitations_service()
        
        assert str(exc_info.value) == "Database connection error"
        mock_get_list_of_recitations.assert_called_once_with(type=TextType.RECITATION)

    @patch('pecha_api.recitations.recitations_services.Text.get_list_of_recitations')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_correct_text_type_filter(
        self,
        mock_get_list_of_recitations
    ):
        """Test that the service correctly filters by TextType.RECITATION."""
        mock_get_list_of_recitations.return_value = []
        
        await get_list_of_recitations_service()
        
        mock_get_list_of_recitations.assert_called_once_with(type=TextType.RECITATION)

    @patch('pecha_api.recitations.recitations_services.Text.get_list_of_recitations')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_dto_mapping(
        self,
        mock_get_list_of_recitations
    ):
        """Test that Text objects are correctly mapped to RecitationDTO objects."""
        text_id = uuid4()
        mock_text = TestDataFactory.create_mock_text(
            text_id=text_id,
            title="Test Mapping Recitation"
        )
        
        mock_get_list_of_recitations.return_value = [mock_text]
        
        result = await get_list_of_recitations_service()
        
        assert len(result.recitations) == 1
        recitation_dto = result.recitations[0]
        
        assert hasattr(recitation_dto, 'title')
        assert hasattr(recitation_dto, 'text_id')
        assert recitation_dto.title == mock_text.title
        assert recitation_dto.text_id == mock_text.id
        
        assert not hasattr(recitation_dto, 'language')
        assert not hasattr(recitation_dto, 'group_id')
        assert not hasattr(recitation_dto, 'is_published')

    @patch('pecha_api.recitations.recitations_services.Text.get_list_of_recitations')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_response_structure(
        self,
        mock_get_list_of_recitations
    ):
        """Test that the response has the correct structure."""
        mock_recitations = [
            TestDataFactory.create_mock_text(title="Recitation 1"),
            TestDataFactory.create_mock_text(title="Recitation 2")
        ]
        mock_get_list_of_recitations.return_value = mock_recitations
        
        result = await get_list_of_recitations_service()
        
        assert isinstance(result, RecitationsResponse)
        assert hasattr(result, 'recitations')
        assert isinstance(result.recitations, list)
        
        for recitation in result.recitations:
            assert isinstance(recitation, RecitationDTO)
            assert hasattr(recitation, 'title')
            assert hasattr(recitation, 'text_id')
            assert isinstance(recitation.title, str)
            assert recitation.text_id is not None
