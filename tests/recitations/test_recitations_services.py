import pytest
from unittest.mock import patch
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
    @patch('pecha_api.recitations.recitations_services.apply_search_recitation_title_filter')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_success(
        self,
        mock_apply_search_filter,
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
        text_id = str(uuid4())
        text_title = "Test Recitation"
        mock_get_root_text.return_value = (text_id, text_title)
        mock_apply_search_filter.return_value = text_title
        
        # Execute
        result = await get_list_of_recitations_service(language="en")
        
        # Verify
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 1
        assert len(result.recitations) == 1
        
        recitation = result.recitations[0]
        assert isinstance(recitation, RecitationDTO)
        assert recitation.title == text_title
        assert str(recitation.text_id) == text_id
        recitation = result.recitations[0]
        assert isinstance(recitation, RecitationDTO)
        assert recitation.title == text_title
        assert str(recitation.text_id) == text_id
        
        # Verify mock calls
        mock_get_collection_id.assert_called_once_with(slug="Liturgy")
        mock_get_root_text.assert_called_once_with(collection_id=liturgy_collection_id, language="en")
        mock_apply_search_filter.assert_called_once_with(text_title=text_title, search=None)
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
    @patch('pecha_api.recitations.recitations_services.apply_search_recitation_title_filter')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_search_filter_no_match(
    async def test_get_list_of_recitations_service_search_filter_no_match(
        self,
        mock_apply_search_filter,
        mock_apply_search_filter,
        mock_get_root_text,
        mock_get_collection_id
    ):
        """Test get_list_of_recitations_service when search filter returns no match."""
        """Test get_list_of_recitations_service when search filter returns no match."""
        liturgy_collection_id = str(uuid4())
        mock_get_collection_id.return_value = liturgy_collection_id
        
        text_id = str(uuid4())
        text_title = "Test Recitation"
        mock_get_root_text.return_value = (text_id, text_title)
        mock_apply_search_filter.return_value = None
        text_id = str(uuid4())
        text_title = "Test Recitation"
        mock_get_root_text.return_value = (text_id, text_title)
        mock_apply_search_filter.return_value = None
        
        result = await get_list_of_recitations_service(search="nonexistent", language="en")
        result = await get_list_of_recitations_service(search="nonexistent", language="en")
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 0
        assert result.recitations == []
        
        mock_get_collection_id.assert_called_once_with(slug="Liturgy")
        mock_get_root_text.assert_called_once_with(collection_id=liturgy_collection_id, language="en")
        mock_apply_search_filter.assert_called_once_with(text_title=text_title, search="nonexistent")
        mock_get_root_text.assert_called_once_with(collection_id=liturgy_collection_id, language="en")
        mock_apply_search_filter.assert_called_once_with(text_title=text_title, search="nonexistent")

    @patch('pecha_api.recitations.recitations_services.get_collection_id_by_slug')
    @patch('pecha_api.recitations.recitations_services.get_root_text_by_collection_id')
    @patch('pecha_api.recitations.recitations_services.apply_search_recitation_title_filter')
    @patch('pecha_api.recitations.recitations_services.apply_search_recitation_title_filter')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_with_search_match(
    async def test_get_list_of_recitations_service_with_search_match(
        self,
        mock_apply_search_filter,
        mock_apply_search_filter,
        mock_get_root_text,
        mock_get_collection_id
    ):
        """Test get_list_of_recitations_service when search filter matches."""
        """Test get_list_of_recitations_service when search filter matches."""
        liturgy_collection_id = str(uuid4())
        mock_get_collection_id.return_value = liturgy_collection_id
        
        text_id = str(uuid4())
        text_title = "Morning Prayer Recitation"
        mock_get_root_text.return_value = (text_id, text_title)
        mock_apply_search_filter.return_value = text_title
        text_title = "Morning Prayer Recitation"
        mock_get_root_text.return_value = (text_id, text_title)
        mock_apply_search_filter.return_value = text_title
        
        result = await get_list_of_recitations_service(search="morning", language="en")
        result = await get_list_of_recitations_service(search="morning", language="en")
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 1
        assert result.recitations[0].title == text_title
        assert str(result.recitations[0].text_id) == text_id
        assert result.recitations[0].title == text_title
        assert str(result.recitations[0].text_id) == text_id
        
        mock_get_collection_id.assert_called_once_with(slug="Liturgy")
        mock_get_root_text.assert_called_once_with(collection_id=liturgy_collection_id, language="en")
        mock_apply_search_filter.assert_called_once_with(text_title=text_title, search="morning")
        mock_get_root_text.assert_called_once_with(collection_id=liturgy_collection_id, language="en")
        mock_apply_search_filter.assert_called_once_with(text_title=text_title, search="morning")

    @patch('pecha_api.recitations.recitations_services.get_collection_id_by_slug')
    @patch('pecha_api.recitations.recitations_services.get_root_text_by_collection_id')
    @patch('pecha_api.recitations.recitations_services.apply_search_recitation_title_filter')
    @patch('pecha_api.recitations.recitations_services.apply_search_recitation_title_filter')
    @pytest.mark.asyncio
    async def test_get_list_of_recitations_service_different_languages(
        self,
        mock_apply_search_filter,
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
        text_title = "Tibetan Recitation"
        mock_get_root_text.return_value = (text_id, text_title)
        mock_apply_search_filter.return_value = text_title
        
        result = await get_list_of_recitations_service(language="bo")
        
        assert isinstance(result, RecitationsResponse)
        assert len(result.recitations) == 1
        assert result.recitations[0].title == text_title
        assert result.recitations[0].title == text_title
        
        # Verify language is passed correctly
        mock_get_root_text.assert_called_once_with(collection_id=liturgy_collection_id, language="bo")
        mock_apply_search_filter.assert_called_once_with(text_title=text_title, search=None)
        mock_get_root_text.assert_called_once_with(collection_id=liturgy_collection_id, language="bo")
        mock_apply_search_filter.assert_called_once_with(text_title=text_title, search=None)
        mock_get_root_text.assert_called_once_with(collection_id=collection.id, language="bo")


class TestGetRecitationDetailsService:
    """Test cases for get_recitation_details_service function."""

   
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
    @patch('pecha_api.recitations.recitations_services.get_all_texts_by_group_id')
    @patch('pecha_api.recitations.recitations_services.TextUtils.filter_text_on_root_and_version')
    @pytest.mark.asyncio
    async def test_get_recitation_details_service_root_text_not_found(
        self,
        mock_filter_texts_root_version,
        mock_get_all_texts_by_group_id,
        mock_get_text_details_by_text_id,
        mock_validate_text_exists,
    ):
        mock_validate_text_exists.return_value = True
        main_text_id = str(uuid4())
        main_text = MagicMock(id=main_text_id, title="Main Title", group_id="group-1")
        mock_get_text_details_by_text_id.return_value = main_text
        mock_get_all_texts_by_group_id.return_value = [MagicMock()]
        mock_filter_texts_root_version.return_value = {"root_text": None}

        req = RecitationDetailsRequest(language="en", recitation=["en"], translations=[], transliterations=[], adaptations=[])
        with pytest.raises(HTTPException) as exc_info:
            await get_recitation_details_service(text_id=main_text_id, recitation_details_request=req)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorConstants.TEXT_NOT_FOUND_MESSAGE


class TestSegmentsMappingByToc:
    """Test cases for _segments_mapping_by_toc function."""

    @staticmethod
    def create_mock_table_of_content(text_id: str = None, segment_ids: list = None) -> TableOfContent:
        """Create a mock TableOfContent object."""
        text_id = text_id or str(uuid4())
        segment_ids = segment_ids or [str(uuid4())]
        
        segments = [
            TextSegment(segment_id=segment_id, segment_number=i+1)
            for i, segment_id in enumerate(segment_ids)
        ]
        
        section = Section(
            id=str(uuid4()),
            title="Test Section",
            section_number=1,
            segments=segments
        )
        
        return TableOfContent(
            id=str(uuid4()),
            text_id=text_id,
            sections=[section]
        )

    @staticmethod
    def create_mock_segment_dto(segment_id: str = None, content: str = "Test content") -> SegmentDTO:
        """Create a mock SegmentDTO object."""
        return SegmentDTO(
            id=segment_id or str(uuid4()),
            text_id=str(uuid4()),
            content=content,
            type="root"
        )

    @staticmethod
    def create_mock_text_dto(text_id: str = None, language: str = "en") -> TextDTO:
        """Create a mock TextDTO object."""
        return TextDTO(
            id=text_id or str(uuid4()),
            title="Test Text",
            language=language,
            group_id=str(uuid4()),
            type="root",
            is_published=True,
            created_date="2023-01-01",
            updated_date="2023-01-01",
            published_date="2023-01-01",
            published_by=str(uuid4())
        )

    @staticmethod
    def create_mock_segment_translation(segment_id: str, language: str = "en", content: str = "Translation content") -> SegmentTranslation:
        """Create a mock SegmentTranslation object."""
        return SegmentTranslation(
            segment_id=segment_id,
            text_id=str(uuid4()),
            title="Translation Title",
            source="test_source",
            language=language,
            content=content
        )

    @staticmethod
    def create_mock_segment_transliteration(segment_id: str, language: str = "bo", content: str = "Transliteration content") -> SegmentTransliteration:
        """Create a mock SegmentTransliteration object."""
        return SegmentTransliteration(
            segment_id=segment_id,
            text_id=str(uuid4()),
            title="Transliteration Title",
            source="test_source",
            language=language,
            content=content
        )

    @staticmethod
    def create_mock_segment_adaptation(segment_id: str, language: str = "en", content: str = "Adaptation content") -> SegmentAdaptation:
        """Create a mock SegmentAdaptation object."""
        return SegmentAdaptation(
            segment_id=segment_id,
            text_id=str(uuid4()),
            title="Adaptation Title",
            source="test_source",
            language=language,
            content=content
        )

    @patch('pecha_api.recitations.recitations_services.get_text_details_by_text_id')
    @patch('pecha_api.recitations.recitations_services.get_segment_by_id')
    @patch('pecha_api.recitations.recitations_services.get_related_mapped_segments')
    @patch('pecha_api.recitations.recitations_services.SegmentUtils.filter_segment_mapping_by_type_or_text_id')
    @pytest.mark.asyncio
    async def test_segments_mapping_by_toc_empty_table_of_contents(
        self,
        mock_filter_segments,
        mock_get_related_segments,
        mock_get_segment,
        mock_get_text_details
    ):
        """Test mapping with empty table of contents."""
        request = RecitationDetailsRequest(
            language="en",
            recitation=["en"],
            translations=[],
            transliterations=[],
            adaptations=[]
        )

        # Execute
        result = await _segments_mapping_by_toc([], request)

        # Verify
        assert len(result) == 0
        assert result == []
        
        # Verify no mock calls were made
        mock_get_text_details.assert_not_called()
        mock_get_segment.assert_not_called()
        mock_get_related_segments.assert_not_called()
        mock_filter_segments.assert_not_called()

class TestFilterByTypeAndLanguage:
    """Test cases for _filter_by_type_and_language function."""

    def test_filter_by_type_and_language_translations(self):
        """Test filtering translations by language."""
        segment_id = str(uuid4())
        items = [
            SegmentTranslation(
                segment_id=segment_id,
                text_id=str(uuid4()),
                title="English Translation",
                source="test",
                language="en",
                content="English content"
            ),
            SegmentTranslation(
                segment_id=segment_id,
                text_id=str(uuid4()),
                title="Tibetan Translation",
                source="test",
                language="bo",
                content="Tibetan content"
            )
        ]
        languages = ["en"]
        
        result = _filter_by_type_and_language(
            key=RecitationListTextType.TRANSLATIONS.value,
            items=items,
            languages=languages
        )
        
        assert len(result) == 1
        assert "en" in result
        assert "bo" not in result
        assert result["en"].content == "English content"

    @patch('pecha_api.recitations.recitations_services.SegmentUtils.apply_bophono')
    def test_filter_by_type_and_language_tibetan_transliteration(self, mock_apply_bophono):
        """Test filtering with bophono application for Tibetan transliterations."""
        mock_apply_bophono.return_value = "Bophono applied content"
        
        segment_id = str(uuid4())
        items = [
            SegmentTransliteration(
                segment_id=segment_id,
                text_id=str(uuid4()),
                title="Tibetan Transliteration",
                source="test",
                language="bo",
                content="Original Tibetan content"
            )
        ]
        languages = ["bo"]
        
        result = _filter_by_type_and_language(
            key=RecitationListTextType.TRANSLITERATIONS.value,
            items=items,
            languages=languages
        )
        
        assert len(result) == 1
        assert "bo" in result
        assert result["bo"].content == "Bophono applied content"
        mock_apply_bophono.assert_called_once_with(segmentContent="Original Tibetan content")

    def test_filter_by_type_and_language_non_tibetan_transliteration(self):
        """Test filtering transliterations for non-Tibetan languages (no bophono)."""
        segment_id = str(uuid4())
        items = [
            SegmentTransliteration(
                segment_id=segment_id,
                text_id=str(uuid4()),
                title="English Transliteration",
                source="test",
                language="en",
                content="English transliteration content"
            )
        ]
        languages = ["en"]
        
        result = _filter_by_type_and_language(
            key=RecitationListTextType.TRANSLITERATIONS.value,
            items=items,
            languages=languages
        )
        
        assert len(result) == 1
        assert "en" in result
        assert result["en"].content == "English transliteration content"

    def test_filter_by_type_and_language_empty_items(self):
        """Test filtering with empty items list."""
        result = _filter_by_type_and_language(
            key=RecitationListTextType.TRANSLATIONS.value,
            items=[],
            languages=["en"]
        )
        
        assert len(result) == 0
        assert result == {}

    def test_filter_by_type_and_language_no_matching_languages(self):
        """Test filtering when no items match requested languages."""
        segment_id = str(uuid4())
        items = [
            SegmentTranslation(
                segment_id=segment_id,
                text_id=str(uuid4()),
                title="French Translation",
                source="test",
                language="fr",
                content="French content"
            )
        ]
        languages = ["en", "bo"]  # Request different languages
        
        result = _filter_by_type_and_language(
            key=RecitationListTextType.TRANSLATIONS.value,
            items=items,
            languages=languages
        )
        
        assert len(result) == 0
        assert result == {}