from elasticsearch import AsyncElasticsearch
from ..config import get

_search_client = None

async def search_client() -> AsyncElasticsearch:
    global _search_client
    if _search_client is None:
        elasticsearch_url = get("ELASTICSEARCH_URL")
        _es_client = AsyncElasticsearch(
            hosts=[elasticsearch_url]
        )
    return _search_client

async def close_search_client():
    """Close search client connection"""
    global _search_client
    if _search_client is not None:
        await _search_client.close()
        _search_client = None