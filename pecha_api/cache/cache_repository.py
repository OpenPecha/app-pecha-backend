from cachetools import TTLCache
from pecha_api.constants import Constants

cache = TTLCache(maxsize=Constants.MAX_CACHE_SIZE, ttl=Constants.CACHE_TTL)

def set_cache(hash_key: str, value: any):
    cache[hash_key] = value

def get_cache_data(hash_key: str):
    if hash_key in cache:
        return cache.get(hash_key)
    return None

    