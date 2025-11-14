import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
from fastapi import HTTPException
from starlette import status

from pecha_api.recitations.recitations_services import (
    get_list_of_recitations_service,
    get_recitation_details_service,
)
from pecha_api.recitations.recitations_response_models import (
    RecitationDTO,
    RecitationsResponse,
    RecitationDetailsRequest,
)
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


class TestGetRecitationDetailsService:
    """Test cases for get_recitation_details_service function."""

    @patch('pecha_api.recitations.recitations_services.TextUtils.validate_text_exists')
    @patch('pecha_api.recitations.recitations_services.get_text_details_by_text_id')
    @patch('pecha_api.recitations.recitations_services.get_texts_by_group_id')
    @patch('pecha_api.recitations.recitations_services.TextUtils.filter_text_on_root_and_version')
    @patch('pecha_api.recitations.recitations_services.get_contents_by_id')
    @patch('pecha_api.recitations.recitations_services.get_segment_by_id')
    @patch('pecha_api.recitations.recitations_services.get_related_mapped_segments')
    @patch('pecha_api.recitations.recitations_services.SegmentUtils.filter_segment_mapping_by_type_or_text_id')
    @pytest.mark.asyncio
    async def test_get_recitation_details_service_success(
        self,
        mock_filter_segments_by_type,
        mock_get_related_mapped_segments,
        mock_get_segment_by_id,
        mock_get_contents_by_id,
        mock_filter_texts_root_version,
        mock_get_texts_by_group_id,
        mock_get_text_details_by_text_id,
        mock_validate_text_exists,
    ):
        mock_validate_text_exists.return_value = True

        # First call (main text details), second call (toc text language)
        main_text_id = str(uuid4())
        main_text = MagicMock(id=main_text_id, title="Main Title", group_id="group-1")
        toc_text = MagicMock(language="en")
        mock_get_text_details_by_text_id.side_effect = [main_text, toc_text]

        # Group texts and root filtering
        mock_get_texts_by_group_id.return_value = [MagicMock()]
        root_text = MagicMock(id="root-text-id")
        mock_filter_texts_root_version.return_value = {"root_text": root_text}

        # TOC with one section and one segment
        segment_id = str(uuid4())
        toc_segment = MagicMock(segment_id=segment_id)
        toc_section = MagicMock(segments=[toc_segment])
        toc_entry = MagicMock(text_id="toc-text-id", sections=[toc_section])
        mock_get_contents_by_id.return_value = [toc_entry]

        # Segment detail for base text
        mock_get_segment_by_id.return_value = MagicMock(content="Base content EN")

        # Related mapped segments and filtering
        mock_get_related_mapped_segments.return_value = [MagicMock()]
        # Return values for each type call: version, transliteration, adaptation
        recitation_item = MagicMock(language="bo", segment_id=str(uuid4()), content="Recitation BO")
        translation_item = MagicMock(language="en", segment_id=str(uuid4()), content="Translation EN")
        mock_filter_segments_by_type.side_effect = [
            [recitation_item],      # for "version" used as "recitation"
            [translation_item],     # for "version" translations
            [],                     # transliterations
            [],                     # adaptations
        ]

        req = RecitationDetailsRequest(
            language="en",
            recitation=["bo"],
            translations=["en"],
            transliterations=[],
            adaptations=[],
        )

        resp = await get_recitation_details_service(text_id=main_text_id, recitation_details_request=req)

        assert resp.text_id is not None
        assert str(resp.text_id) == main_text_id
        assert resp.title == "Main Title"
        assert len(resp.segments) == 1

        seg = resp.segments[0]
        # Recitation should include "bo" from filtered items
        assert "bo" in seg.recitation
        assert seg.recitation["bo"].content == "Recitation BO"
        # Translations should be empty when no mapped version matches requested languages
        assert seg.translations == {}
        # Others empty
        assert seg.transliterations == {}
        assert seg.adaptations == {}

        mock_validate_text_exists.assert_called_once_with(text_id=main_text_id)
        mock_get_texts_by_group_id.assert_awaited_once()
        mock_filter_texts_root_version.assert_called_once()
        mock_get_contents_by_id.assert_awaited_once_with(text_id=root_text.id)

    @patch('pecha_api.recitations.recitations_services.TextUtils.validate_text_exists')
    @pytest.mark.asyncio
    async def test_get_recitation_details_service_text_not_found(self, mock_validate_text_exists):
        mock_validate_text_exists.return_value = False
        req = RecitationDetailsRequest(language="en", recitation=["en"], translations=[], transliterations=[], adaptations=[])
        with pytest.raises(HTTPException) as exc_info:
            await get_recitation_details_service(text_id=str(uuid4()), recitation_details_request=req)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE

    @patch('pecha_api.recitations.recitations_services.TextUtils.validate_text_exists')
    @patch('pecha_api.recitations.recitations_services.get_text_details_by_text_id')
    @patch('pecha_api.recitations.recitations_services.get_texts_by_group_id')
    @patch('pecha_api.recitations.recitations_services.TextUtils.filter_text_on_root_and_version')
    @pytest.mark.asyncio
    async def test_get_recitation_details_service_root_text_not_found(
        self,
        mock_filter_texts_root_version,
        mock_get_texts_by_group_id,
        mock_get_text_details_by_text_id,
        mock_validate_text_exists,
    ):
        mock_validate_text_exists.return_value = True
        main_text_id = str(uuid4())
        main_text = MagicMock(id=main_text_id, title="Main Title", group_id="group-1")
        mock_get_text_details_by_text_id.return_value = main_text
        mock_get_texts_by_group_id.return_value = [MagicMock()]
        mock_filter_texts_root_version.return_value = {"root_text": None}

        req = RecitationDetailsRequest(language="en", recitation=["en"], translations=[], transliterations=[], adaptations=[])
        with pytest.raises(HTTPException) as exc_info:
            await get_recitation_details_service(text_id=main_text_id, recitation_details_request=req)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE