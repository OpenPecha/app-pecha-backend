import pytest
from unittest.mock import patch, AsyncMock

from pecha_api.search.search_views import (
    search
)

from pecha_api.search.search_response_models import (
    SearchResponse,
    SourceResultItem,
    SheetResultItem,
    TextIndex,
    SegmentMatch,
    Search
)

from pecha_api.search.search_enums import SearchType

@pytest.mark.asyncio
async def test_search_type_source_success():
    mock_search_query = Search(
        text="query",
        type=SearchType.SOURCE
    )
    mock_source_result_item = [
        SourceResultItem(
            text=TextIndex(
                text_id=f"text_id_{i}",
                language="en",
                title="title",
                published_date="2021-01-01"
            ),
            segment_match=[
                SegmentMatch(
                    segment_id=f"segment_id_{i}",
                    content="content"
                )
            ]
        )
        for i in range(1,6)
    ]
    mock_search_results = SearchResponse(
        search=mock_search_query,
        sources=mock_source_result_item,
        skip=0,
        limit=10,
        total=5
    )
    
    with patch("pecha_api.search.search_views.get_search_results", new_callable=AsyncMock, return_value=mock_search_results):
        
        response = await search(query="query", search_type=SearchType.SOURCE, skip=0, limit=10)
    
        assert response is not None
        assert isinstance(response, SearchResponse)
        assert response.search is not None
        assert response.search.text == "query"
        assert response.search.type == SearchType.SOURCE
        assert response.sources is not None
        assert len(response.sources) == 5
        assert response.sources[0] is not None
        assert isinstance(response.sources[0], SourceResultItem)
        assert response.sources[0].text is not None
        assert response.sources[0].text.text_id == "text_id_1"
        assert response.sources[0].text.language == "en"