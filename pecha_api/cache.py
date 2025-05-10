from cachetools import TTLCache
from pecha_api.constants import Constants
import hashlib

from pecha_api.texts.texts_response_models import DetailTableOfContentResponse

cache = TTLCache(maxsize=Constants.MAX_CACHE_SIZE, ttl=Constants.CACHE_TTL)

def get_text_details_cache(text_id: str = None, content_id: str = None, segment_id: str = None, version_id: str = None, section_id: str = None):

    # Concatenate all parameters into a single string
    params_str = f"{text_id}{content_id}{segment_id}{version_id}{section_id}"

    # Generate a hash value using SHA-256
    hash_value = hashlib.sha256(params_str.encode()).hexdigest()
    if hash_value in cache:
        return cache.get(hash_value)
    return None

def set_text_details_cache(text_id: str = None, content_id: str = None, segment_id: str = None, version_id: str = None, section_id: str = None, text_details: DetailTableOfContentResponse = None):
    params_str = f"{text_id}{content_id}{segment_id}{version_id}{section_id}"
    hash_value = hashlib.sha256(params_str.encode()).hexdigest()
    cache[hash_value] = text_details