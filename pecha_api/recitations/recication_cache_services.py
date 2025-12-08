from pecha_api.cache.cache_enums import CacheType
from pecha_api.utils import Utils
from pecha_api import config
from pecha_api.recitations.recitations_response_models import RecitationDetailsResponse
from pecha_api.cache.cache_repository import set_cache, get_cache_data

async def set_recitation_by_text_id_cache(text_id: str = None, language: str = None, cache_type: CacheType = None, data: RecitationDetailsResponse = None):
    """Set recitation by text_id cache asynchronously."""
    payload = [text_id, language, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_time_out = config.get_int("CACHE_TEXT_TIMEOUT")
    await set_cache(hash_key=hashed_key, value=data, cache_time_out=cache_time_out)

async def get_recitation_by_text_id_cache(text_id: str = None, language: str = None, cache_type: CacheType = None) -> RecitationDetailsResponse:
    """Get text by text id or collection cache asynchronously."""
    payload = [text_id, language, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: RecitationDetailsResponse = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = RecitationDetailsResponse(**cache_data)
    return cache_data