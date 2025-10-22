from pecha_api import config
from pecha_api.cache.cache_repository import (
    get_cache_data,
    set_cache,
    update_cache,
    delete_cache,
)
from pecha_api.utils import Utils
from .user_response_models import (
    UserInfoResponse
)
from pecha_api.cache.cache_enums import CacheType

async def get_user_info_cache(token: str, cache_type: CacheType = None) -> UserInfoResponse:
    """Get user info cache asynchronously."""
    payload = [token, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: UserInfoResponse = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = UserInfoResponse(**cache_data)
    return cache_data

async def set_user_info_cache(token: str, data: UserInfoResponse, cache_type: CacheType = None):
    """Set user info cache asynchronously."""
    payload = [token, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_time_out = config.get_int("CACHE_TEXT_TIMEOUT")
    await set_cache(hash_key=hashed_key, value=data, cache_time_out=cache_time_out)


async def update_user_info_cache(token: str, data: UserInfoResponse, cache_type: CacheType = None) -> bool:
    
    payload = [token, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_time_out = config.get_int("CACHE_TEXT_TIMEOUT")
    # Try to update existing cache entry
    is_updated: bool = await update_cache(hash_key=hashed_key, value=data, cache_time_out=cache_time_out)
    if is_updated:
        return True
    # If update failed (e.g., key missing), delete existing cache entry to avoid stale data
    return await delete_cache(hash_key=hashed_key)

async def update_user_avatar_cache(token: str, data: UserInfoResponse, cache_type: CacheType = None) -> bool:
    payload = [token, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_time_out = config.get_int("CACHE_TEXT_TIMEOUT")
    # Try to update existing cache entry
    is_updated: bool = await update_cache(hash_key=hashed_key, value=data, cache_time_out=cache_time_out)
    if is_updated:
        return True
    # If update failed (e.g., key missing), delete existing cache entry to avoid stale data
    return await delete_cache(hash_key=hashed_key)