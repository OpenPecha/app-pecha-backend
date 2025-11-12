import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
from fastapi import HTTPException
from starlette import status

from pecha_api.recitations.recitations_services import get_list_of_recitations_service
from pecha_api.recitations.recitations_response_models import RecitationDTO, RecitationsResponse
from pecha_api.error_contants import ErrorConstants


class TestDataFactory:
    """Factory class for creating test data objects."""
    
    @staticmethod
    def create_mock_collection(collection_id=None, slug="test-collection"):
        """Create a mock Collection object with specified attributes."""
        mock_collection = MagicMock()
        mock_collection.id = collection_id or str(uuid4())
        mock_collection.slug = slug
        return mock_collection


class TestGetListOfRecitationsService:
    """Test cases for get_list_of_recitations_service function."""

    @patch('pecha_api.recitations.recitations_services.get_collection_id_by_slug')
    @patch('pecha_api.recitations.recitations_services.get_all_collections_by_parent')
    @patch('pecha_api.recitations.recitations_services.get_root_text_by_collection_id')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_success(
        self,
        mock_get_root_text,
        mock_get_all_collections,
        mock_get_collection_id
    ):
        """Test successful retrieval of recitations list."""
        # Setup mocks
        liturgy_collection_id = str(uuid4())
        mock_get_collection_id.return_value = liturgy_collection_id
        
        collection_1 = TestDataFactory.create_mock_collection(collection_id=str(uuid4()))
        collection_2 = TestDataFactory.create_mock_collection(collection_id=str(uuid4()))
        mock_get_all_collections.return_value = [collection_1, collection_2]
        
        text_id_1 = str(uuid4())
        text_id_2 = str(uuid4())
        mock_get_root_text.side_effect = [
            (text_id_1, "First Recitation"),
            (text_id_2, "Second Recitation")
        ]
        
        # Execute
        result = await get_list_of_recitations_service(language="en")
        
        # Verify
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 2
        
        first_recitation = result.recitations[0]
        assert isinstance(first_recitation, RecitationDTO)
        assert first_recitation.title == "First Recitation"
        assert str(first_recitation.text_id) == text_id_1
        
        second_recitation = result.recitations[1]
        assert isinstance(second_recitation, RecitationDTO)
        assert second_recitation.title == "Second Recitation"
        assert str(second_recitation.text_id) == text_id_2
        
        # Verify mock calls
        mock_get_collection_id.assert_called_once_with(slug="Liturgy")
        mock_get_all_collections.assert_called_once_with(parent_id=liturgy_collection_id)
        assert mock_get_root_text.call_count == 2
        mock_get_root_text.assert_any_call(collection_id=collection_1.id, language="en")
        mock_get_root_text.assert_any_call(collection_id=collection_2.id, language="en")

    @patch('pecha_api.recitations.recitations_services.get_collection_id_by_slug')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_collection_not_found(
        self,
        mock_get_collection_id
    ):
        """Test get_list_of_recitations_service when Liturgy collection is not found."""
        mock_get_collection_id.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_list_of_recitations_service(language="en")
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.COLLECTION_NOT_FOUND
        mock_get_collection_id.assert_called_once_with(slug="Liturgy")

    @patch('pecha_api.recitations.recitations_services.get_collection_id_by_slug')
    @patch('pecha_api.recitations.recitations_services.get_all_collections_by_parent')
    @patch('pecha_api.recitations.recitations_services.get_root_text_by_collection_id')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_empty_collections(
        self,
        mock_get_root_text,
        mock_get_all_collections,
        mock_get_collection_id
    ):
        """Test get_list_of_recitations_service when no child collections exist."""
        liturgy_collection_id = str(uuid4())
        mock_get_collection_id.return_value = liturgy_collection_id
        mock_get_all_collections.return_value = []
        
        result = await get_list_of_recitations_service(language="en")
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 0
        assert result.recitations == []
        
        mock_get_collection_id.assert_called_once_with(slug="Liturgy")
        mock_get_all_collections.assert_called_once_with(parent_id=liturgy_collection_id)
        mock_get_root_text.assert_not_called()

    @patch('pecha_api.recitations.recitations_services.get_collection_id_by_slug')
    @patch('pecha_api.recitations.recitations_services.get_all_collections_by_parent')
    @patch('pecha_api.recitations.recitations_services.get_root_text_by_collection_id')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_no_texts_found(
        self,
        mock_get_root_text,
        mock_get_all_collections,
        mock_get_collection_id
    ):
        """Test get_list_of_recitations_service when collections exist but no texts are found."""
        liturgy_collection_id = str(uuid4())
        mock_get_collection_id.return_value = liturgy_collection_id
        
        collection_1 = TestDataFactory.create_mock_collection()
        collection_2 = TestDataFactory.create_mock_collection()
        mock_get_all_collections.return_value = [collection_1, collection_2]
        
        # Mock get_root_text to return None for both collections
        mock_get_root_text.side_effect = [(None, None), (None, None)]
        
        result = await get_list_of_recitations_service(language="en")
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 0
        assert result.recitations == []
        
        mock_get_collection_id.assert_called_once_with(slug="Liturgy")
        mock_get_all_collections.assert_called_once_with(parent_id=liturgy_collection_id)
        assert mock_get_root_text.call_count == 2

    @patch('pecha_api.recitations.recitations_services.get_collection_id_by_slug')
    @patch('pecha_api.recitations.recitations_services.get_all_collections_by_parent')
    @patch('pecha_api.recitations.recitations_services.get_root_text_by_collection_id')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_partial_texts_found(
        self,
        mock_get_root_text,
        mock_get_all_collections,
        mock_get_collection_id
    ):
        """Test get_list_of_recitations_service when only some collections have texts."""
        liturgy_collection_id = str(uuid4())
        mock_get_collection_id.return_value = liturgy_collection_id
        
        collection_1 = TestDataFactory.create_mock_collection()
        collection_2 = TestDataFactory.create_mock_collection()
        collection_3 = TestDataFactory.create_mock_collection()
        mock_get_all_collections.return_value = [collection_1, collection_2, collection_3]
        
        text_id = str(uuid4())
        # Only collection_2 has a text
        mock_get_root_text.side_effect = [
            (None, None),  # collection_1 has no text
            (text_id, "Found Recitation"),  # collection_2 has text
            (None, None)   # collection_3 has no text
        ]
        
        result = await get_list_of_recitations_service(language="bo")
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 1
        
        recitation = result.recitations[0]
        assert isinstance(recitation, RecitationDTO)
        assert recitation.title == "Found Recitation"
        assert str(recitation.text_id) == text_id
        
        mock_get_collection_id.assert_called_once_with(slug="Liturgy")
        mock_get_all_collections.assert_called_once_with(parent_id=liturgy_collection_id)
        assert mock_get_root_text.call_count == 3

    @patch('pecha_api.recitations.recitations_services.get_collection_id_by_slug')
    @patch('pecha_api.recitations.recitations_services.get_all_collections_by_parent')
    @patch('pecha_api.recitations.recitations_services.get_root_text_by_collection_id')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_different_languages(
        self,
        mock_get_root_text,
        mock_get_all_collections,
        mock_get_collection_id
    ):
        """Test get_list_of_recitations_service with different language parameters."""
        liturgy_collection_id = str(uuid4())
        mock_get_collection_id.return_value = liturgy_collection_id
        
        collection = TestDataFactory.create_mock_collection()
        mock_get_all_collections.return_value = [collection]
        
        text_id = str(uuid4())
        mock_get_root_text.return_value = (text_id, "Tibetan Recitation")
        
        result = await get_list_of_recitations_service(language="bo")
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 1
        assert result.recitations[0].title == "Tibetan Recitation"
        
        # Verify language is passed correctly
        mock_get_root_text.assert_called_once_with(collection_id=collection.id, language="bo")