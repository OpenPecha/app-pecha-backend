from pecha_api.utils import Utils

from pecha_api.cache.cache_repository import (
    get_cache_data,
    set_cache
)

from .search_enums import (
    SearchType
)

from .search_response_models import (
    SearchResponse
)

def get_search_results_cache(query: str = None, search_type: SearchType = None, text_id: str = None, skip: int = 0, limit: int = 10):
    payload = [query, search_type, text_id, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_search_results_cache(query: str = None, search_type: SearchType = None, text_id: str = None, skip: int = 0, limit: int = 10, data: SearchResponse = None):
    payload = [query, search_type, text_id, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)