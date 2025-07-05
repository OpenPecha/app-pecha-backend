import hashlib

from pecha_api.texts.texts_response_models import (
    DetailTableOfContentResponse,
    TextsCategoryResponse,
    TableOfContentResponse,
    TextVersionResponse
)
from pecha_api.texts.segments.segments_response_models import (
    SegmentDTO,
    SegmentInfoResponse,
    SegmentRootMappingResponse,
    SegmentTranslationsResponse,
    SegmentCommentariesResponse
)

from typing import List, Union

from .cache_repository import (
    set_cache,
    get_cache_data
)

def generate_hash_key(payload: List[Union[str, int]]) -> str:

    params_str = "".join(str(param) for param in payload)
    hash_value = hashlib.sha256(params_str.encode()).hexdigest()
    return hash_value

# TEXTS

def set_text_details_cache(text_id: str = None, content_id: str = None, version_id: str = None, skip: int = None, limit: int = None, data: DetailTableOfContentResponse = None):
    payload = [text_id, content_id, version_id, skip, limit]
    hashed_key: str = generate_hash_key(payload = payload)
    set_cache(hash_key =hashed_key, value = data)


def get_text_details_cache(text_id: str = None, content_id: str = None, version_id: str = None, skip: int = None, limit: int = None):
    payload = [text_id, content_id, version_id, skip, limit]
    hashed_key: str = generate_hash_key(payload = payload)
    cache_data = get_cache_data(hash_key =hashed_key)
    return cache_data

def get_text_by_text_id_or_term_cache(text_id: str = None, term_id: str = None, language: str = None, skip: int = None, limit: int = None):
    payload = [text_id, term_id, language, skip, limit]
    hashed_key: str = generate_hash_key(payload = payload)
    cache_data = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_text_by_text_id_or_term_cache(text_id: str = None, term_id: str = None, language: str = None, skip: int = None, limit: int = None, data: TextsCategoryResponse = None):
    payload = [text_id, term_id, language, skip, limit]
    hashed_key: str = generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)

def get_table_of_contents_by_text_id_cache(text_id: str = None):
    payload = [text_id]
    hashed_key: str = generate_hash_key(payload = payload)
    cache_data = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_table_of_contents_by_text_id_cache(text_id: str = None, data: TableOfContentResponse = None):
    payload = [text_id]
    hashed_key: str = generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)

def get_text_versions_by_group_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None):
    payload = [text_id, language, skip, limit]
    hashed_key: str = generate_hash_key(payload = payload)
    cache_data = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_text_versions_by_group_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None, data: TextVersionResponse = None):
    payload = [text_id, language, skip, limit]
    hashed_key: str = generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)


# SEGMENTS
def get_segment_details_by_id_cache(segment_id: str = None, text_details: bool = None):
    payload = [segment_id, text_details]
    hashed_key: str = generate_hash_key(payload = payload)
    cache_data = get_cache_data(hash_key=hashed_key)
    return cache_data

def set_segment_details_by_id_cache(segment_id: str = None, text_details: bool = None, data: SegmentDTO = None):
    payload = [segment_id, text_details]
    hashed_key: str = generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value=data)

def get_segment_info_by_id_cache(segment_id: str = None):
    payload = [segment_id]
    hashed_key: str = generate_hash_key(payload = payload)
    cache_data = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_segment_info_by_id_cache(segment_id: str = None, data: SegmentInfoResponse = None):
    payload = [segment_id]
    hashed_key: str = generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)

def get_segment_root_mapping_by_id_cache(segment_id: str = None):
    payload = [segment_id]
    hashed_key: str = generate_hash_key(payload = payload)
    cache_data = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_segment_root_mapping_by_id_cache(segment_id: str = None, data: SegmentRootMappingResponse = None):
    payload = [segment_id]
    hashed_key: str = generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)

def get_segment_translations_by_id_cache(segment_id: str = None):
    payload = [segment_id]
    hashed_key: str = generate_hash_key(payload = payload)
    cache_data = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_segment_translations_by_id_cache(segment_id: str = None, data: SegmentTranslationsResponse = None):
    payload = [segment_id]
    hashed_key: str = generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)

def get_segment_commentaries_by_id_cache(segment_id: str = None):
    payload = [segment_id]
    hashed_key: str = generate_hash_key(payload = payload)
    cache_data = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_segment_commentaries_by_id_cache(segment_id: str = None, data: SegmentCommentariesResponse = None):
    payload = [segment_id]
    hashed_key: str = generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)