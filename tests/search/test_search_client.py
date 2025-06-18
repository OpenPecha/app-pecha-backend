import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from elastic_transport import ConnectionError
from fastapi import HTTPException
from pecha_api.search import search_client as search_client_module
from pecha_api.search.search_client import search_client, close_search_client
import elastic_transport
from pecha_api.config import get

@pytest.mark.asyncio
async def test_search_client_success():
    mock_es = AsyncMock()
    mock_es_class = AsyncMock(return_value=mock_es)
    with patch('pecha_api.search.search_client.AsyncElasticsearch', mock_es_class):
        with patch('pecha_api.search.search_client.get', side_effect=lambda key: {
            'ELASTICSEARCH_URL': 'test_elasticsearch_url',
            'ELASTICSEARCH_API': 'test_api_key'
        }[key]):
            # First call should create new client
            client = await search_client()
            assert client == mock_es
            mock_es_class.assert_called_once_with(
                hosts=['test_elasticsearch_url'],
                api_key='test_api_key'
            )

@pytest.mark.asyncio
async def test_search_client_close_success():
    mock_es = MagicMock()
    mock_es.close = AsyncMock()
    # Patch the global _search_client directly in the module
    with patch('pecha_api.search.search_client._search_client', mock_es):
        with patch('pecha_api.search.search_client.get', side_effect=lambda key: {
            'ELASTICSEARCH_URL': 'test_elasticsearch_url',
            'ELASTICSEARCH_API': 'test_api_key'
        }[key]):
            await close_search_client()
            mock_es.close.assert_awaited_once()
