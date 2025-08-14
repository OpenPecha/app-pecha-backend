import json
from typing import Any, Optional, List

from redis.asyncio import Redis

from pecha_api import config
from pecha_api.cache.cache_enums import CacheType
import logging
from pydantic.json import pydantic_encoder


_client: Optional[Redis] = None


def get_client() -> Redis:
    """Get or create Redis client instance"""
    global _client
    if _client is None:
        redis_url = config.get("CACHE_CONNECTION_STRING")
        _client = Redis.from_url(redis_url)
    return _client


def _build_key(key: str) -> str:
    """Build cache key with prefix"""
    prefix = config.get("CACHE_PREFIX")
    return f"{prefix}{key}"



async def set_cache(hash_key: str, value: Any, cache_time_out: int) -> bool:
    #Set value in cache with type-specific timeout
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        if not isinstance(value, (str, bytes)):
            value = json.dumps(value, default=pydantic_encoder)
        return bool(await client.setex(full_key, cache_time_out, value))
    except Exception:
        logging.error("An error occurred in set_cache", exc_info=True)
        return False


async def get_cache_data(hash_key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        value = await client.get(full_key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from cache", exc_info=True)
            return value
    except Exception:
        logging.error("An error occurred in get_cache_data", exc_info=True)
        return None


async def delete_cache(hash_key: str) -> bool:
    """Delete key from cache"""
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        return bool(await client.delete(full_key))
    except Exception:
        logging.error("An error occurred in delete_cache", exc_info=True)
        return False


async def exists_in_cache(hash_key: str) -> bool:
    """Check if key exists in cache"""
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        return bool(await client.exists(full_key))
    except Exception:
        logging.error("An error occurred in exists_in_cache", exc_info=True)
        return False

async def clear_cache(hash_key: str = None):
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        return bool(await client.delete(full_key))
    except Exception:
        logging.error("An error occurred in clear_cache", exc_info=True)
        return False


async def update_cache(hash_key: str, value: Any, cache_time_out: str = "CACHE_DEFAULT_TIMEOUT") -> bool:
    """Update existing cache entry with new value, resetting TTL to type-specific timeout"""
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        
        # Check if key exists
        if not await client.exists(full_key):
            logging.warning(f"Cache key {hash_key} does not exist, cannot update")
            return False
        
        # Serialize value
        if not isinstance(value, (str, bytes)):
            value = json.dumps(value, default=pydantic_encoder)
        
        timeout = config.get_int(cache_time_out)
        return bool(await client.setex(full_key, timeout, value))
    except Exception:
        logging.error("An error occurred in update_cache", exc_info=True)
        return False


async def invalidate_cache_entries(text_id: Optional[str] = None, hash_keys: Optional[List[str]] = None) -> bool:
    try:
        client = get_client()
        
        # Validate input parameters
        if text_id and hash_keys:
            raise ValueError("Cannot specify both text_id and hash_keys. Use one or the other.")
        if not text_id and not hash_keys:
            raise ValueError("Must specify either text_id or hash_keys.")
        
        keys_to_delete = []
        
        if text_id:
            # Pattern-based invalidation for text_id
            prefix = config.get("CACHE_PREFIX")
            pattern = f"{prefix}{text_id}"
            keys_to_delete = await client.keys(pattern)
            operation_type = f"text_id: {text_id}"
        else:
            # Specific hash keys invalidation
            if not hash_keys:
                return True
            
            # Build full keys
            full_keys = [_build_key(key) for key in hash_keys]
            
            # Filter out non-existent keys
            for key in full_keys:
                if await client.exists(key):
                    keys_to_delete.append(key)
            
            operation_type = f"{len(hash_keys)} hash keys"
        
        if keys_to_delete:
            deleted_count = await client.delete(*keys_to_delete)
            logging.info(f"Invalidated {deleted_count} cache entries for {operation_type}")
            return deleted_count > 0
        
        logging.info(f"No cache entries found for {operation_type}")
        return True
        
    except Exception:
        error_context = f"text_id: {text_id}" if text_id else "multiple cache keys"
        logging.error(f"An error occurred while invalidating cache for {error_context}", exc_info=True)
        return False


async def invalidate_text_related_cache(text_id: str) -> bool:
    """Invalidate all cache entries related to a specific text_id"""
    return await invalidate_cache_entries(text_id=text_id)


async def invalidate_multiple_cache_keys(hash_keys: List[str]) -> bool:
    """Invalidate multiple cache entries by their hash keys"""
    return await invalidate_cache_entries(hash_keys=hash_keys)