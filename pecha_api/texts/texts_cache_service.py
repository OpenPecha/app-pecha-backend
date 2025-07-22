
from pecha_api.utils import Utils

from pecha_api.cache.cache_repository import (
    get_cache_data,
    set_cache
)
from .texts_response_models import (
    DetailTableOfContentResponse,
    TextsCategoryResponse,
    TableOfContentResponse,
    TextVersionResponse,
    TextDTO
)

async def set_text_details_cache(text_id: str = None, content_id: str = None, version_id: str = None, skip: int = None, limit: int = None, data: DetailTableOfContentResponse = None):
    """Set text details cache asynchronously."""
    payload = [text_id, content_id, version_id, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key =hashed_key, value = data)

async def get_text_details_cache(text_id: str = None, content_id: str = None, version_id: str = None, skip: int = None, limit: int = None) -> DetailTableOfContentResponse:
    """Get text details cache asynchronously."""
    payload = [text_id, content_id, version_id, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: DetailTableOfContentResponse = await get_cache_data(hash_key =hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = DetailTableOfContentResponse(**cache_data)
    return cache_data

async def get_text_by_text_id_or_term_cache(text_id: str = None, term_id: str = None, language: str = None, skip: int = None, limit: int = None) -> TextsCategoryResponse | TextDTO:
    """Get text by text id or term cache asynchronously."""
    payload = [text_id, term_id, language, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: TextsCategoryResponse | TextDTO = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = TextsCategoryResponse(**cache_data)
    return cache_data

async def set_text_by_text_id_or_term_cache(text_id: str = None, term_id: str = None, language: str = None, skip: int = None, limit: int = None, data: TextsCategoryResponse = None):
    """Set text by text id or term cache asynchronously."""
    payload = [text_id, term_id, language, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)

async def get_table_of_contents_by_text_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None) -> TableOfContentResponse:
    """Get table of contents by text id cache asynchronously."""
    payload = [text_id, language, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: TableOfContentResponse = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = TableOfContentResponse(**cache_data)
    return cache_data

async def set_table_of_contents_by_text_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None, data: TableOfContentResponse = None):
    """Set table of contents by text id cache asynchronously."""
    payload = [text_id, language, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)

async def get_text_versions_by_group_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None) -> TextVersionResponse:
    """Get text versions by group id cache asynchronously."""
    payload = [text_id, language, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: TextVersionResponse = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = TextVersionResponse(**cache_data)
    return cache_data

async def set_text_versions_by_group_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None, data: TextVersionResponse = None):
    """Set text versions by group id cache asynchronously."""
    payload = [text_id, language, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)