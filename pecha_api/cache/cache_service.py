import hashlib

from pecha_api.texts.texts_response_models import (
    TextDetailsRequest
)


from .cache_repository import (
    set_cache,
    get_cache_data
)

def generate_key(text_id: str, content_id: str, skip: int, limit: int):
    params_str = f"{text_id}{content_id}{skip}{limit}"
    hash_value = hashlib.sha256(params_str.encode()).hexdigest()
    return hash_value

async def set_text_details_cache(text_id: str = None, content_id: str = None, skip: int = None, limit: int = None,
                                 text_details: DetailTableOfContentResponse = None):
    hashed_key = generate_key(text_id, content_id, skip, limit)
    await set_cache(hashed_key, text_details)


async def get_text_details_cache(text_id: str = None, content_id: str = None, skip: int = None, limit: int = None):
    hashed_key = generate_key(text_id, content_id, skip, limit)
    cache_data = await get_cache_data(hashed_key)
    return cache_data


