from pecha_api.utils import Utils
from pecha_api.cache.cache_repository import (
    get_cache_data,
    set_cache,
    clear_cache
)
from .segments_response_models import (
    SegmentDTO,
    SegmentInfoResponse,
    SegmentRootMappingResponse,
    SegmentTranslationsResponse,
    SegmentCommentariesResponse
)
from typing import Dict, List
from pecha_api.cache.cache_enums import CacheType

# SEGMENTS
async def get_segment_details_by_id_cache(segment_id: str = None, text_details: bool = None) -> SegmentDTO:
    payload = [segment_id, text_details]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: SegmentDTO = await get_cache_data(hash_key=hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = SegmentDTO(**cache_data)
    return cache_data

async def set_segment_details_by_id_cache(segment_id: str = None, text_details: bool = None, data: SegmentDTO = None):
    payload = [segment_id, text_details]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value=data)

async def get_segment_info_by_id_cache(segment_id: str = None, cache_type: CacheType = None) -> SegmentInfoResponse:
    payload = [segment_id, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: SegmentInfoResponse = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = SegmentInfoResponse(**cache_data)
    return cache_data

async def set_segment_info_by_id_cache(segment_id: str = None, cache_type: CacheType = None, data: SegmentInfoResponse = None):
    payload = [segment_id, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)

async def get_segment_root_mapping_by_id_cache(segment_id: str = None) -> SegmentRootMappingResponse:
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: SegmentRootMappingResponse = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = SegmentRootMappingResponse(**cache_data)
    return cache_data

async def set_segment_root_mapping_by_id_cache(segment_id: str = None, data: SegmentRootMappingResponse = None):
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)

async def get_segment_translations_by_id_cache(segment_id: str = None) -> SegmentTranslationsResponse:
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: SegmentTranslationsResponse = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = SegmentTranslationsResponse(**cache_data)
    return cache_data

async def set_segment_translations_by_id_cache(segment_id: str = None, data: SegmentTranslationsResponse = None):
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)

async def get_segment_commentaries_by_id_cache(segment_id: str = None) -> SegmentCommentariesResponse:
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: SegmentCommentariesResponse = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = SegmentCommentariesResponse(**cache_data)
    return cache_data

async def set_segment_commentaries_by_id_cache(segment_id: str = None, data: SegmentCommentariesResponse = None):
    payload = [segment_id]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)


async def get_segments_details_by_ids_cache(segment_ids: List[str] = None, cache_type: CacheType = None) -> Dict[str, SegmentDTO]:
    payload = list(segment_ids) + [cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: Dict[str, SegmentDTO] = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = {k: SegmentDTO(**v) for k, v in cache_data.items()}
    return cache_data

async def set_segments_details_by_ids_cache(segment_ids: List[str] = None, cache_type: CacheType = None, data: Dict[str, SegmentDTO] = None):
    payload = list(segment_ids) + [cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)

async def delete_segments_details_by_ids_cache(segment_ids: List[str] = None, cache_type: CacheType = None):
    payload = list(segment_ids) + [cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await clear_cache(hash_key = hashed_key)