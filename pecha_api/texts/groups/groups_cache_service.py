from pecha_api.utils import Utils

from pecha_api.cache.cache_repository import (
    get_cache_data,
    set_cache
)

from .groups_response_models import (
    GroupDTO
)

def get_group_by_id_cache(group_id: str = None):
    payload = [group_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_group_by_id_cache(group_id: str = None, data: GroupDTO = None):
    payload = [group_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)