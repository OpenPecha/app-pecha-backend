from pecha_api.utils import Utils

from pecha_api.cache.cache_repository import (
    get_cache_data,
    set_cache
)

from .groups_response_models import (
    GroupDTO
)

async def get_group_by_id_cache(group_id: str = None) -> GroupDTO:
    """Get group by id cache asynchronously."""
    payload = [group_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: GroupDTO = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = GroupDTO(**cache_data)
    return cache_data

async def set_group_by_id_cache(group_id: str = None, data: GroupDTO = None):
    """Set group by id cache asynchronously."""
    payload = [group_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)