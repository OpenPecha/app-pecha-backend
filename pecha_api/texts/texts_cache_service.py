
from pecha_api.utils import Utils

from pecha_api.cache.cache_repository import (
    get_cache_data,
    set_cache,
    clear_cache,
    update_cache,
    invalidate_text_related_cache,
    invalidate_multiple_cache_keys
)
from .texts_response_models import (
    DetailTableOfContentResponse,
    TextsCategoryResponse,
    TableOfContentResponse,
    TextVersionResponse,
    TextDTO,
    TableOfContent
)
from pecha_api.cache.cache_enums import CacheType

from typing import Optional
import logging

async def set_text_details_cache(text_id: str = None, content_id: str = None, version_id: str = None, skip: int = None, limit: int = None, data: DetailTableOfContentResponse = None, cache_type: CacheType = None):
    """Set text details cache asynchronously."""
    payload = [text_id, content_id, version_id, skip, limit, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key =hashed_key, value = data)

async def get_text_details_cache(text_id: str = None, content_id: str = None, version_id: str = None, skip: int = None, limit: int = None, cache_type: CacheType = None) -> DetailTableOfContentResponse:
    """Get text details cache asynchronously."""
    payload = [text_id, content_id, version_id, skip, limit, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: DetailTableOfContentResponse = await get_cache_data(hash_key =hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = DetailTableOfContentResponse(**cache_data)
    return cache_data


async def get_text_by_text_id_or_collection_cache(text_id: str = None, collection_id: str = None, language: str = None, skip: int = None, limit: int = None, cache_type: CacheType = None) -> TextsCategoryResponse | TextDTO:
    """Get text by text id or collection cache asynchronously."""
    payload = [text_id, collection_id, language, skip, limit, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: TextsCategoryResponse | TextDTO = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = TextsCategoryResponse(**cache_data)
    return cache_data


async def set_text_by_text_id_or_collection_cache(text_id: str = None, collection_id: str = None, language: str = None, skip: int = None, limit: int = None, cache_type: CacheType = None, data: TextsCategoryResponse = None):
    """Set text by text id or collection cache asynchronously."""
    payload = [text_id, collection_id, language, skip, limit, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)

async def get_table_of_contents_by_text_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None, cache_type: CacheType = None) -> TableOfContentResponse:
    """Get table of contents by text id cache asynchronously."""
    payload = [text_id, language, skip, limit, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: TableOfContentResponse = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = TableOfContentResponse(**cache_data)
    return cache_data

async def set_table_of_contents_by_text_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None, data: TableOfContentResponse = None, cache_type: CacheType = None):
    """Set table of contents by text id cache asynchronously."""
    payload = [text_id, language, skip, limit, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)

async def get_table_of_content_by_sheet_id_cache(sheet_id: str = None, cache_type: CacheType = None) -> Optional[TableOfContent]:
    payload = [sheet_id, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: TableOfContent = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = TableOfContent(**cache_data)
    return cache_data

async def set_table_of_content_by_sheet_id_cache(sheet_id: str = None, cache_type: CacheType = None, data: TableOfContent = None):
    payload = [sheet_id, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)
    
async def delete_table_of_content_by_sheet_id_cache(sheet_id: str = None, cache_type: CacheType = None):
    payload = [sheet_id, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await clear_cache(hash_key = hashed_key)

async def get_text_versions_by_group_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None, cache_type: CacheType = None) -> TextVersionResponse:
    """Get text versions by group id cache asynchronously."""
    payload = [text_id, language, skip, limit, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: TextVersionResponse = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = TextVersionResponse(**cache_data)
    return cache_data

async def set_text_versions_by_group_id_cache(text_id: str = None, language: str = None, skip: int = None, limit: int = None, cache_type: CacheType = None, data: TextVersionResponse = None):
    """Set text versions by group id cache asynchronously."""
    payload = [text_id, language, skip, limit, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)

async def set_text_details_by_id_cache(text_id: str = None, cache_type: CacheType = None, data: TextDTO = None):
    payload = [text_id, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await set_cache(hash_key = hashed_key, value = data)

async def get_text_details_by_id_cache(text_id: str = None, cache_type: CacheType = None) -> TextDTO:
    payload = [text_id, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    cache_data: TextDTO = await get_cache_data(hash_key = hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = TextDTO(**cache_data)
    return cache_data

async def delete_text_details_by_id_cache(text_id: str = None, cache_type: CacheType = None):
    payload = [text_id, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload = payload)
    await clear_cache(hash_key = hashed_key)


async def update_text_details_cache(text_id: str, updated_text_data: TextDTO) -> bool:
    #Update cached text details for a specific text_id with new data
    try:
        # Update TEXT_DETAIL cache if it exists
        text_detail_payload = [text_id, CacheType.TEXT_DETAIL]
        text_detail_hash_key = Utils.generate_hash_key(payload=text_detail_payload)
        
        # Update TEXTS_BY_ID_OR_COLLECTION cache if it exists (this caches individual text details)
        texts_by_id_payload = [text_id, None, None, None, None, CacheType.TEXTS_BY_ID_OR_COLLECTION]
        texts_by_id_hash_key = Utils.generate_hash_key(payload=texts_by_id_payload)
        
        # Try to update existing cache entries
        update_results = []
        
        # Update text detail cache
        is_text_detail_updated = await update_cache(hash_key=text_detail_hash_key, value=updated_text_data)
        update_results.append(is_text_detail_updated)
        
        # Update texts by id cache
        is_texts_by_id_updated = await update_cache(hash_key=texts_by_id_hash_key, value=updated_text_data)
        update_results.append(is_texts_by_id_updated)
        
        # If direct updates failed, fallback to invalidation to ensure cache consistency
        if not any(update_results):
            await invalidate_text_related_cache(text_id=text_id)
            
        return True
    except Exception as e:
        logging.error(f"Error updating text details cache for text_id {text_id}: {str(e)}", exc_info=True)
        # Fallback to cache invalidation to maintain consistency
        await invalidate_text_related_cache(text_id=text_id)
        return False


async def invalidate_text_cache_on_update(text_id: str) -> bool:
    #Invalidate all cache entries related to a text when it's updated
    try:
        # Generate hash keys for all possible cache entries related to this text
        cache_keys_to_invalidate = []
        
        # TEXT_DETAIL cache
        text_detail_payload = [text_id, CacheType.TEXT_DETAIL]
        cache_keys_to_invalidate.append(Utils.generate_hash_key(payload=text_detail_payload))
        
        # TEXTS_BY_ID_OR_COLLECTION cache (individual text)
        texts_by_id_payload = [text_id, None, None, None, None, CacheType.TEXTS_BY_ID_OR_COLLECTION]
        cache_keys_to_invalidate.append(Utils.generate_hash_key(payload=texts_by_id_payload))
        
        # TEXT_TABLE_OF_CONTENTS cache
        toc_payload = [text_id, None, None, None, CacheType.TEXT_TABLE_OF_CONTENTS]
        cache_keys_to_invalidate.append(Utils.generate_hash_key(payload=toc_payload))
        
        # TEXT_VERSIONS cache
        versions_payload = [text_id, None, None, None, CacheType.TEXT_VERSIONS]
        cache_keys_to_invalidate.append(Utils.generate_hash_key(payload=versions_payload))
        
        # Invalidate specific cache keys
        await invalidate_multiple_cache_keys(hash_keys=cache_keys_to_invalidate)
        
        # Also do a broader invalidation to catch any cache entries we might have missed
        await invalidate_text_related_cache(text_id=text_id)
        
        return True
    except Exception as e:
        logging.error(f"Error invalidating cache for text_id {text_id}: {str(e)}", exc_info=True)
        return False