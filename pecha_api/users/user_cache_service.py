from pecha_api.cache.cache_repository import (
    get_cache_data,
    set_cache
)
from pecha_api.utils import Utils
from .user_response_models import (
    UserInfoResponse
)

async def get_user_info_cache(token: str) -> UserInfoResponse:
    """Get user info cache asynchronously."""
    payload = [token]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: UserInfoResponse = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = UserInfoResponse(**cache_data)
    return cache_data

async def set_user_info_cache(token: str, data: UserInfoResponse):
    """Set user info cache asynchronously."""
    payload = [token]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)