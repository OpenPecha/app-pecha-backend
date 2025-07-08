import pytest
from unittest.mock import patch, AsyncMock, Mock, MagicMock

from pecha_api.search.search_response_models import (
    SearchResponse,
    SourceResultItem,
    SheetResultItem,
    TextIndex,
    SegmentMatch,
    SearchType
)
from pecha_api.search.search_service import (
    get_search_results
)

@pytest.mark.asyncio
async def test_get_search_results_for_source_success():

    mock_elastic_response = _get_mock_elastic_source_response_()

    mock_client = Mock()
    mock_client.search = AsyncMock(return_value=mock_elastic_response)

    with patch("pecha_api.search.search_service.search_client", new_callable=Mock, return_value=mock_client), \
        patch("pecha_api.search.search_service.get_search_results_cache", new_callable=MagicMock, return_value=None), \
        patch("pecha_api.search.search_service.set_search_results_cache", new_callable=MagicMock):
        response = await get_search_results(query="query", search_type=SearchType.SOURCE, skip=0, limit=2)

        assert response is not None
        assert isinstance(response, SearchResponse)
        assert response.sheets == []
        assert response.sources != []
        assert response.sources[0] is not None
        assert isinstance(response.sources[0], SourceResultItem)
        assert response.sources[0].text is not None
        assert response.sources[0].text.text_id == "e6370d09-aa0c-4a41-96ef-deffb89c7810"
        assert response.sources[0].text.language == "en"
        assert response.sources[0].text.title == "The Way of the Bodhisattva Claude AI Draft"
        assert response.sources[0].segment_match is not None
        assert len(response.sources[0].segment_match) == 2
        assert isinstance(response.sources[0].segment_match[0], SegmentMatch)
        assert response.sources[0].segment_match[0].segment_id == "2eb76906-f2d5-48ca-9f80-2023ee6b3ad0"
        assert response.search is not None
        assert response.search.text == "query"
        assert response.search.type == SearchType.SOURCE

@pytest.mark.asyncio
async def test_get_search_results_for_sheet_success():
    mock_sheet_search = [
        SheetResultItem(
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

    with patch("pecha_api.search.search_service._mock_sheet_data_", new_callable=Mock, return_value=mock_sheet_search), \
        patch("pecha_api.search.search_service.get_search_results_cache", new_callable=MagicMock, return_value=None), \
        patch("pecha_api.search.search_service.set_search_results_cache", new_callable=MagicMock):

        response = await get_search_results(query="query", search_type=SearchType.SHEET)

        assert response is not None
        assert isinstance(response, SearchResponse)
        assert response.sources == []
        assert response.sheets != []
        assert len(response.sheets) == 5
        assert response.sheets[0] is not None
        assert isinstance(response.sheets[0], SheetResultItem)
        assert response.sheets[0].sheet_title == mock_sheet_search[0].sheet_title
        assert response.sheets[0].sheet_summary == mock_sheet_search[0].sheet_summary
        assert response.sheets[0].publisher_id == mock_sheet_search[0].publisher_id
        assert response.sheets[0].sheet_id == mock_sheet_search[0].sheet_id


@pytest.mark.asyncio
async def test_get_search_results_for_source_within_text_success():
    text_id = "e6370d09-aa0c-4a41-96ef-deffb89c7810"
    mock_elastic_response = _get_mock_elastic_source_within_text_response_()
    mock_client = Mock()
    mock_client.search = AsyncMock(return_value=mock_elastic_response)

    with patch("pecha_api.search.search_service.search_client", new_callable=Mock, return_value=mock_client), \
        patch("pecha_api.search.search_service.get_search_results_cache", new_callable=MagicMock, return_value=None), \
        patch("pecha_api.search.search_service.set_search_results_cache", new_callable=MagicMock):

        response = await get_search_results(query="query", search_type=SearchType.SOURCE, text_id=text_id, skip=0, limit=10)

        assert response is not None
        assert isinstance(response, SearchResponse)
        assert response.sources != []
        assert len(response.sources) == 1
        assert response.sources[0] is not None
        assert isinstance(response.sources[0], SourceResultItem)
        assert response.sources[0].text is not None
        assert response.sources[0].text.text_id == text_id



def _get_mock_elastic_source_response_():
    return {
        "took": 8,
        "timed_out": False,
        "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
        "hits": {
            "total": {"value": 148, "relation": "eq"},
            "max_score": 3.0705519,
            "hits": [
                {
                    "_index": "pecha-segments",
                    "_id": "aLygYpcB3z3vvVmz7u8a",
                    "_score": 3.0705519,
                    "_source": {
                        "id": "2eb76906-f2d5-48ca-9f80-2023ee6b3ad0",
                        "content": "May all beings hear the sound of Dharma<br>Unceasingly from birds and trees,<br>From all rays of light,<br>And even from the sky itself.",
                        "text_id": "e6370d09-aa0c-4a41-96ef-deffb89c7810",
                        "text": {
                            "title": "The Way of the Bodhisattva Claude AI Draft",
                            "language": "en",
                            "parent_id": "032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
                            "is_published": "true",
                            "created_date": "2025-04-05 04:38:34.436250+00:00",
                            "updated_date": "2025-04-05 04:38:34.436269+00:00",
                            "published_date": "2025-04-05 04:38:34.436287+00:00",
                            "published_by": "pecha",
                            "type": "version",
                            "group_id": "6bdc5225-63c2-4c97-b87f-d68be0b601b3"
                        }
                    }
                },
                {
                    "_index": "pecha-segments",
                    "_id": "u7ygYpcB3z3vvVmz6u2g",
                    "_score": 2.8719563,
                    "_source": {
                        "id": "8d3bc31e-9591-4d67-ab5b-36a239701b10",
                        "content": "Suffering, mental distress,<br>Various forms of fear,<br>And separation from desires -<br>These arise from engaging in harmful actions.",
                        "text_id": "e6370d09-aa0c-4a41-96ef-deffb89c7810",
                        "text": {
                            "title": "The Way of the Bodhisattva Claude AI Draft",
                            "language": "en",
                            "parent_id": "032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
                            "is_published": "true",
                            "created_date": "2025-04-05 04:38:34.436250+00:00",
                            "updated_date": "2025-04-05 04:38:34.436269+00:00",
                            "published_date": "2025-04-05 04:38:34.436287+00:00",
                            "published_by": "pecha",
                            "type": "version",
                            "group_id": "6bdc5225-63c2-4c97-b87f-d68be0b601b3"
                        }
                    }
                }
            ]
        }
    }

def _get_mock_elastic_source_within_text_response_():
    return {
        "took": 8,
        "timed_out": False,
        "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
        "hits": {
            "total": {"value": 148, "relation": "eq"},
            "max_score": 3.0705519,
            "hits": [
                {
                    "_index": "pecha-segments",
                    "_id": "aLygYpcB3z3vvVmz7u8a",
                    "_score": 3.0705519,
                    "_source": {
                        "id": "2eb76906-f2d5-48ca-9f80-2023ee6b3ad0",
                        "content": "May all beings hear the sound of Dharma<br>Unceasingly from birds and trees,<br>From all rays of light,<br>And even from the sky itself.",
                        "text_id": "e6370d09-aa0c-4a41-96ef-deffb89c7810",
                        "text": {
                            "title": "The Way of the Bodhisattva Claude AI Draft",
                            "language": "en",
                            "parent_id": "032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
                            "is_published": "true",
                            "created_date": "2025-04-05 04:38:34.436250+00:00",
                            "updated_date": "2025-04-05 04:38:34.436269+00:00",
                            "published_date": "2025-04-05 04:38:34.436287+00:00",
                            "published_by": "pecha",
                            "type": "version",
                            "group_id": "6bdc5225-63c2-4c97-b87f-d68be0b601b3"
                        }
                    }
                },
                {
                    "_index": "pecha-segments",
                    "_id": "u7ygYpcB3z3vvVmz6u2g",
                    "_score": 2.8719563,
                    "_source": {
                        "id": "8d3bc31e-9591-4d67-ab5b-36a239701b10",
                        "content": "Suffering, mental distress,<br>Various forms of fear,<br>And separation from desires -<br>These arise from engaging in harmful actions.",
                        "text_id": "e6370d09-aa0c-4a41-96ef-deffb89c7810",
                        "text": {
                            "title": "The Way of the Bodhisattva Claude AI Draft",
                            "language": "en",
                            "parent_id": "032b9a5f-0712-40d8-b7ec-73c8c94f1c15",
                            "is_published": "true",
                            "created_date": "2025-04-05 04:38:34.436250+00:00",
                            "updated_date": "2025-04-05 04:38:34.436269+00:00",
                            "published_date": "2025-04-05 04:38:34.436287+00:00",
                            "published_by": "pecha",
                            "type": "version",
                            "group_id": "6bdc5225-63c2-4c97-b87f-d68be0b601b3"
                        }
                    }
                }
            ]
        }
    }