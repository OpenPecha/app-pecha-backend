import pytest
from unittest.mock import patch, AsyncMock, Mock, MagicMock
from pecha_api.topics.topics_cache_service import (
    get_topics_cache,
    set_topics_cache
)
from pecha_api.topics.topics_response_models import (
    TopicsResponse,
    TopicModel,
    CreateTopicRequest
)

@pytest.mark.asyncio
async def test_get_topics_cache_empty_cache():
    with patch("pecha_api.topics.topics_cache_service.get_cache_data", return_value=None):
        response = get_topics_cache(parent_id="parent_id", language="language", search="search", hierarchy=True, skip=0, limit=10)
        assert response is None

@pytest.mark.asyncio
async def test_get_topics_cache_success():
    mock_cache_data = TopicsResponse(
        parent=None, 
        topics=[], 
        total=0, 
        skip=0, 
        limit=10
    )
    with patch("pecha_api.topics.topics_cache_service.get_cache_data", return_value=mock_cache_data):
        response = get_topics_cache(parent_id="parent_id", language="language", search="search", hierarchy=True, skip=0, limit=10)
        assert response is not None
        assert isinstance(response, TopicsResponse)
        assert response.parent is None
        assert response.topics == []
        assert response.total == 0
        assert response.skip == 0
        assert response.limit == 10
    
@pytest.mark.asyncio
async def test_set_topics_cache_success():
    mock_cache_data = TopicsResponse(
        parent=None, 
        topics=[], 
        total=0, 
        skip=0, 
        limit=10
    )
    with patch("pecha_api.topics.topics_cache_service.set_cache", new_callable=Mock):

        response = set_topics_cache(parent_id="parent_id", language="language", search="search", hierarchy=True, skip=0, limit=10, data=mock_cache_data)
        
        