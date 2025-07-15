
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

def set_text_details_cache(text_id: str = None, content_id: str = None, version_id: str = None, skip: int = None, limit: int = None, data: DetailTableOfContentResponse = None):
    payload = [text_id, content_id, version_id, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key =hashed_key, value = data)


def get_text_details_cache(text_id: str = None, content_id: str = None, version_id: str = None, skip: int = None, limit: int = None) -> DetailTableOfContentResponse:
    payload = [text_id, content_id, version_id, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: DetailTableOfContentResponse = get_cache_data(hash_key =hashed_key)
    return cache_data

def get_text_by_text_id_or_term_cache(text_id: str = None, term_id: str = None, language: str = None, skip: int = None, limit: int = None) -> TextsCategoryResponse | TextDTO:
    payload = [text_id, term_id, language, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: TextsCategoryResponse | TextDTO = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_text_by_text_id_or_term_cache(text_id: str = None, term_id: str = None, language: str = None, skip: int = None, limit: int = None, data: TextsCategoryResponse = None):
    payload = [text_id, term_id, language, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)

def get_table_of_contents_by_text_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None) -> TableOfContentResponse:
    payload = [text_id, language, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: TableOfContentResponse = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_table_of_contents_by_text_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None, data: TableOfContentResponse = None):
    payload = [text_id, language, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)

def get_text_versions_by_group_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None) -> TextVersionResponse:
    payload = [text_id, language, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: TextVersionResponse = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_text_versions_by_group_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None, data: TextVersionResponse = None):
    payload = [text_id, language, skip, limit]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)