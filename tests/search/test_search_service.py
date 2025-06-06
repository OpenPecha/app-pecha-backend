import pytest
from unittest.mock import patch, AsyncMock

from pecha_api.search.search_response_models import (
    SearchResponse,
    Source,
    Sheet,
    Text,
    SegmentMatch,
    SearchType
)
from pecha_api.search.search_service import (
    get_search_results
)

@pytest.mark.asyncio
async def test_get_search_results_for_source_success():
    mock_text = Text(
        text_id="text_id_1",
        language="en",
        title="title",
        published_date="12-02-2025"
    )
    mock_segment_match = SegmentMatch(
        segment_id="segment_id_1",
        content="content"
    )
    mock_source = Source(
        text=mock_text,
        segment_match=[
            mock_segment_match
        ]
    )
    mock_search_sources = [
        mock_source
        for i in range(2)
    ]
    with patch("pecha_api.search.search_service._mock_source_data_", new_callable=AsyncMock, return_value=mock_search_sources):
        
        response = await get_search_results(query="query", type=SearchType.SOURCE)

        assert response is not None
        assert isinstance(response, SearchResponse)
        assert response.sheets == []
        assert response.sources != []
        assert len(response.sources) == 2
        assert response.sources[0] is not None
        assert isinstance(response.sources[0], Source)
        assert response.sources[0].text is not None
        assert response.sources[0].text.text_id == mock_text.text_id
        assert response.sources[0].text.language == mock_text.language
        assert response.sources[0].text.title == mock_text.title
        assert response.sources[0].segment_match is not None
        assert len(response.sources[0].segment_match) == 1
        assert isinstance(response.sources[0].segment_match[0], SegmentMatch)
        assert response.sources[0].segment_match[0].segment_id == mock_segment_match.segment_id
        assert response.sources[0].segment_match[0].content == mock_segment_match.content

@pytest.mark.asyncio
async def test_get_search_results_for_sheet_success():
    mock_sheet_search = [
        Sheet(
            sheet_title=f"sheet_title_{i}",
            sheet_summary=f"sheet_summary_{i}",
            publisher_id=i,
            sheet_id=i,
            publisher_name=f"publisher_name_{i}",
            publisher_url=f"publisher_url_{i}",
            publisher_image=f"publisher_image_{i}",
            publisher_position=f"publisher_position_{i}",
            publisher_organization=f"publisher_organization_{i}",
        )
        for i in range(1,6)
    ]

    with patch("pecha_api.search.search_service._mock_sheet_data_", new_callable=AsyncMock, return_value=mock_sheet_search):

        response = await get_search_results(query="query", type=SearchType.SHEET)

        assert response is not None
        assert isinstance(response, SearchResponse)
        assert response.sources == []
        assert response.sheets != []
        assert len(response.sheets) == 5
        assert response.sheets[0] is not None
        assert isinstance(response.sheets[0], Sheet)
        assert response.sheets[0].sheet_title == mock_sheet_search[0].sheet_title
        assert response.sheets[0].sheet_summary == mock_sheet_search[0].sheet_summary
        assert response.sheets[0].publisher_id == mock_sheet_search[0].publisher_id
        assert response.sheets[0].sheet_id == mock_sheet_search[0].sheet_id
