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

def get_topics_cache(parent_id: str = None, language: str = None, search: str = None, hierarchy: bool = None, skip: int = None, limit: int = None) -> TopicsResponse:
    payload = [parent_id, language, search, hierarchy, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: TopicsResponse = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_topics_cache(parent_id: str = None, language: str = None, search: str = None, hierarchy: bool = None, skip: int = None, limit: int = None, data: TopicsResponse = None):
    payload = [parent_id, language, search, hierarchy, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)