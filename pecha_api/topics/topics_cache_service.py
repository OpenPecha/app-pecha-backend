from pecha_api.utils import Utils
from pecha_api.cache.cache_repository import (
    get_cache_data,
    set_cache
)
from .topics_response_models import (
    TopicsResponse,
    TopicModel,
    CreateTopicRequest
)
from pecha_api.cache.cache_enums import CacheType


async def get_topics_cache(parent_id: str = None, language: str = None, search: str = None, hierarchy: bool = None, skip: int = None, limit: int = None, cache_type: CacheType = None) -> TopicsResponse:
    """Get topics cache asynchronously."""
    payload = [parent_id, language, search, hierarchy, skip, limit, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: TopicsResponse = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = TopicsResponse(**cache_data)
    return cache_data

async def set_topics_cache(parent_id: str = None, language: str = None, search: str = None, hierarchy: bool = None, skip: int = None, limit: int = None, data: TopicsResponse = None, cache_type: CacheType = None):
    """Set topics cache asynchronously."""
    payload = [parent_id, language, search, hierarchy, skip, limit, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)