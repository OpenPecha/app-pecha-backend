from pecha_api.utils import Utils
from pecha_api.cache.cache_repository import (
    get_cache_data,
    set_cache
)
from .segments_response_models import (
    SegmentDTO,
    SegmentInfoResponse,
    SegmentRootMappingResponse,
    SegmentTranslationsResponse,
    SegmentCommentariesResponse
)

# SEGMENTS
def get_segment_details_by_id_cache(segment_id: str = None, text_details: bool = None) -> SegmentDTO:
    payload = [segment_id, text_details]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: SegmentDTO = get_cache_data(hash_key=hashed_key)
    return cache_data

def set_segment_details_by_id_cache(segment_id: str = None, text_details: bool = None, data: SegmentDTO = None):
    payload = [segment_id, text_details]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value=data)

def get_segment_info_by_id_cache(segment_id: str = None) -> SegmentInfoResponse:
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: SegmentInfoResponse = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_segment_info_by_id_cache(segment_id: str = None, data: SegmentInfoResponse = None):
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)

def get_segment_root_mapping_by_id_cache(segment_id: str = None) -> SegmentRootMappingResponse:
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: SegmentRootMappingResponse = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_segment_root_mapping_by_id_cache(segment_id: str = None, data: SegmentRootMappingResponse = None):
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)

def get_segment_translations_by_id_cache(segment_id: str = None) -> SegmentTranslationsResponse:
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: SegmentTranslationsResponse = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_segment_translations_by_id_cache(segment_id: str = None, data: SegmentTranslationsResponse = None):
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)

def get_segment_commentaries_by_id_cache(segment_id: str = None) -> SegmentCommentariesResponse:
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: SegmentCommentariesResponse = get_cache_data(hash_key = hashed_key)
    return cache_data

def set_segment_commentaries_by_id_cache(segment_id: str = None, data: SegmentCommentariesResponse = None):
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    set_cache(hash_key = hashed_key, value = data)