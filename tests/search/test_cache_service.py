import pytest
from unittest.mock import patch, Mock, MagicMock

from pecha_api.search.search_cache_service import (
    get_search_cache,
    set_search_cache
)
from pecha_api.search.search_response_models import (
    SearchResponse,
    Search,
    TextIndex,
    SegmentMatch,
    SourceResultItem
)
from pecha_api.search.search_enums import SearchType

@pytest.mark.asyncio
async def test_get_search_cache_empty_cache_for_source_search():
    with patch("pecha_api.search.search_cache_service.get_cache_data", new_callable=Mock, return_value=None):
        response = get_search_cache(query="query", search_type=SearchType.SOURCE, text_id="text_id", skip=0, limit=10)
        
        assert response is None

@pytest.mark.asyncio
async def test_get_search_cache_empty_cache_for_sheet_serach():
    with patch("pecha_api.search.search_cache_service.get_cache_data", new_callable=Mock, return_value=None):
        response = get_search_cache(query="query", search_type=SearchType.SHEET, text_id="text_id", skip=0, limit=10)
        
        assert response is None

@pytest.mark.asyncio
async def test_get_search_cache_for_search_response():
    mock_cache_data = SearchResponse(
        search=Search(
            text="query",
            type=SearchType.SOURCE
        ),
        sources=[
            SourceResultItem(
                text=TextIndex(
                    text_id="text_id",
                    language="en",
                    title="title",
                    published_date="published_date"
                ),
                segment_match=[
                    SegmentMatch(
                        segment_id="segment_id",
                        content="content"
                    )
                ]
            )
        ],
        sheets=[],
        skip=0,
        limit=10,
        total=1
    )
    with patch("pecha_api.search.search_cache_service.get_cache_data", new_callable=Mock, return_value=mock_cache_data):
        
        response = get_search_cache(query="query", search_type=SearchType.SOURCE, text_id="text_id", skip=0, limit=10)

        assert response is not None
        assert isinstance(response, SearchResponse)
        assert response.search is not None
        assert response.search.text == "query"
        assert response.search.type == SearchType.SOURCE
        assert response.sources is not None
        assert len(response.sources) == 1
        assert response.sources[0].text is not None
        assert response.sources[0].text.text_id == "text_id"

@pytest.mark.asyncio
async def test_set_cache_for_search_response():
    mock_cache_data = SearchResponse(
        search=Search(
            text="query",
            type=SearchType.SOURCE
        ),
        sources=[],
        sheets=[],
        skip=0,
        limit=10,
        total=1
    )
    with patch("pecha_api.search.search_cache_service.set_cache", new_callable=Mock):
        
        set_search_cache(query="query", search_type=SearchType.SOURCE, text_id="text_id", skip=0, limit=10, data=mock_cache_data)