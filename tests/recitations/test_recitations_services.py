import pytest
from unittest.mock import patch
from uuid import uuid4
from fastapi import HTTPException
from starlette import status

from pecha_api.recitations.recitations_services import (
    get_list_of_recitations_service,
    get_recitation_details_service,
    _segments_mapping_by_toc,
    _filter_by_type_and_language,
)
from pecha_api.recitations.recitations_response_models import (
    RecitationDTO,
    RecitationsResponse,
    RecitationDetailsRequest,
    RecitationSegment,
    Segment,
)
from pecha_api.texts.texts_response_models import TableOfContent, Section, TextSegment, TextDTO
from pecha_api.texts.segments.segments_response_models import (
    SegmentDTO,
    SegmentTranslation,
    SegmentTransliteration,
    SegmentAdaptation,
)
from pecha_api.recitations.recitations_enum import RecitationListTextType, LanguageCode
from pecha_api.texts.texts_enums import TextType
from pecha_api.error_contants import ErrorConstants


class TestGetListOfRecitationsService:
    """Test cases for get_list_of_recitations_service function."""

    @patch('pecha_api.recitations.recitations_services.get_collection_id_by_slug')
    @patch('pecha_api.recitations.recitations_services.get_root_text_by_collection_id')
    @patch('pecha_api.recitations.recitations_services.apply_search_recitation_title_filter')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_success(
        self,
        mock_apply_search_filter,
        mock_get_root_text,
        mock_get_collection_id
    ):
        """Test successful retrieval of recitations list."""
        # Setup mocks
        liturgy_collection_id = str(uuid4())
        mock_get_collection_id.return_value = liturgy_collection_id
        
        text_id = str(uuid4())
        text_title = "Test Recitation"
        mock_get_root_text.return_value = (text_id, text_title)
        mock_apply_search_filter.return_value = text_title
        
        # Execute
        result = await get_list_of_recitations_service(language="en")
        
        # Verify
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 1
        
        recitation = result.recitations[0]
        assert isinstance(recitation, RecitationDTO)
        assert recitation.title == text_title
        assert str(recitation.text_id) == text_id
        
        # Verify mock calls
        mock_get_collection_id.assert_called_once_with(slug="Liturgy")
        mock_get_root_text.assert_called_once_with(collection_id=liturgy_collection_id, language="en")
        mock_apply_search_filter.assert_called_once_with(text_title=text_title, search=None)

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
    @patch('pecha_api.recitations.recitations_services.get_root_text_by_collection_id')
    @patch('pecha_api.recitations.recitations_services.apply_search_recitation_title_filter')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_search_filter_no_match(
        self,
        mock_apply_search_filter,
        mock_get_root_text,
        mock_get_collection_id
    ):
        """Test get_list_of_recitations_service when search filter returns no match."""
        liturgy_collection_id = str(uuid4())
        mock_get_collection_id.return_value = liturgy_collection_id
        
        text_id = str(uuid4())
        text_title = "Test Recitation"
        mock_get_root_text.return_value = (text_id, text_title)
        mock_apply_search_filter.return_value = None
        
        result = await get_list_of_recitations_service(search="nonexistent", language="en")
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 0
        assert result.recitations == []
        
        mock_get_collection_id.assert_called_once_with(slug="Liturgy")
        mock_get_root_text.assert_called_once_with(collection_id=liturgy_collection_id, language="en")
        mock_apply_search_filter.assert_called_once_with(text_title=text_title, search="nonexistent")

    @patch('pecha_api.recitations.recitations_services.get_collection_id_by_slug')
    @patch('pecha_api.recitations.recitations_services.get_root_text_by_collection_id')
    @patch('pecha_api.recitations.recitations_services.apply_search_recitation_title_filter')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_with_search_match(
        self,
        mock_apply_search_filter,
        mock_get_root_text,
        mock_get_collection_id
    ):
        """Test get_list_of_recitations_service when search filter matches."""
        liturgy_collection_id = str(uuid4())
        mock_get_collection_id.return_value = liturgy_collection_id
        
        text_id = str(uuid4())
        text_title = "Morning Prayer Recitation"
        mock_get_root_text.return_value = (text_id, text_title)
        mock_apply_search_filter.return_value = text_title
        
        result = await get_list_of_recitations_service(search="morning", language="en")
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 1
        assert result.recitations[0].title == text_title
        assert str(result.recitations[0].text_id) == text_id
        
        mock_get_collection_id.assert_called_once_with(slug="Liturgy")
        mock_get_root_text.assert_called_once_with(collection_id=liturgy_collection_id, language="en")
        mock_apply_search_filter.assert_called_once_with(text_title=text_title, search="morning")

    @patch('pecha_api.recitations.recitations_services.get_collection_id_by_slug')
    @patch('pecha_api.recitations.recitations_services.get_root_text_by_collection_id')
    @patch('pecha_api.recitations.recitations_services.apply_search_recitation_title_filter')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_different_languages(
        self,
        mock_apply_search_filter,
        mock_get_root_text,
        mock_get_collection_id
    ):
        """Test get_list_of_recitations_service with different language parameters."""
        liturgy_collection_id = str(uuid4())
        mock_get_collection_id.return_value = liturgy_collection_id
        
        text_id = str(uuid4())
        text_title = "Tibetan Recitation"
        mock_get_root_text.return_value = (text_id, text_title)
        mock_apply_search_filter.return_value = text_title
        
        result = await get_list_of_recitations_service(language="bo")
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 1
        assert result.recitations[0].title == text_title
        
        # Verify language is passed correctly
        mock_get_root_text.assert_called_once_with(collection_id=liturgy_collection_id, language="bo")
        mock_apply_search_filter.assert_called_once_with(text_title=text_title, search=None)