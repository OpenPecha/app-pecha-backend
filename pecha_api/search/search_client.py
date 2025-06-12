from elasticsearch import AsyncElasticsearch
from ..config import get
from pecha_api.error_contants import ErrorConstants
from fastapi import HTTPException

_search_client = None

async def search_client() -> AsyncElasticsearch:
    try:
        global _search_client
        if _search_client is None:
            elasticsearch_url = get("ELASTICSEARCH_URL")
            _search_client = AsyncElasticsearch(
                hosts=[elasticsearch_url],
                api_key= get("ELASTICSEARCH_API")
            )
        return _search_client
    except ConnectionError:
        raise HTTPException(status_code=503, detail=ErrorConstants.ELASTICSEARCH_CONNECTION_ERROR_MESSAGE)

async def close_search_client():
    """Close search client connection"""
    try:
        global _search_client
        if _search_client is not None:
            try:
                await _search_client.close()
            except Exception as e:
                print(f"Error closing Elastic search client: {e}")
            finally:
                _search_client = None
    except ConnectionError:
        raise HTTPException(status_code=503, detail=ErrorConstants.ELASTICSEARCH_CONNECTION_ERROR_MESSAGE)