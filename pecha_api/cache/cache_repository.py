import json
from typing import Any, Optional, List

from redis.asyncio import Redis

from pecha_api import config
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


async def set_cache(hash_key: str, value: Any) -> bool:
    """Set value in cache with default timeout"""
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        timeout = config.get_int("CACHE_DEFAULT_TIMEOUT")
        if not isinstance(value, (str, bytes)):
            value = json.dumps(value, default=pydantic_encoder)
        return bool(await client.setex(full_key, timeout, value))
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


async def update_cache(hash_key: str, value: Any) -> bool:
    #Update existing cache entry with new value, maintaining original TTL if possible
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        
        # Check if key exists
        if not await client.exists(full_key):
            logging.warning(f"Cache key {hash_key} does not exist, cannot update")
            return False
        
        # Get current TTL
        ttl = await client.ttl(full_key)
        if ttl == -1:  # Key exists but has no expiry
            ttl = config.get_int("CACHE_DEFAULT_TIMEOUT")
        elif ttl == -2:  # Key does not exist
            logging.warning(f"Cache key {hash_key} expired during update")
            return False
        
        # Serialize value
        if not isinstance(value, (str, bytes)):
            value = json.dumps(value, default=pydantic_encoder)
        
        # Update with remaining TTL
        return bool(await client.setex(full_key, ttl, value))
    except Exception:
        logging.error("An error occurred in update_cache", exc_info=True)
        return False


async def invalidate_text_related_cache(text_id: str) -> bool:
    Invalidate all cache entries related to a specific text_id
    try:
        client = get_client()
        prefix = config.get("CACHE_PREFIX")
        
        # Pattern to match all cache keys that might contain this text_id
        pattern = f"{prefix}*{text_id}*"
        
        # Get all matching keys
        keys = await client.keys(pattern)
        
        if keys:
            # Delete all matching keys
            deleted_count = await client.delete(*keys)
            logging.info(f"Invalidated {deleted_count} cache entries for text_id: {text_id}")
            return deleted_count > 0
        
        logging.info(f"No cache entries found for text_id: {text_id}")
        return True
    except Exception:
        logging.error(f"An error occurred while invalidating cache for text_id: {text_id}", exc_info=True)
        return False


async def invalidate_multiple_cache_keys(hash_keys: List[str]) -> bool:
    Invalidate multiple cache entries by their hash keys
    try:
        client = get_client()
        
        if not hash_keys:
            return True
        
        # Build full keys
        full_keys = [_build_key(key) for key in hash_keys]
        
        # Filter out non-existent keys
        existing_keys = []
        for key in full_keys:
            if await client.exists(key):
                existing_keys.append(key)
        
        if existing_keys:
            deleted_count = await client.delete(*existing_keys)
            logging.info(f"Invalidated {deleted_count} cache entries")
            return deleted_count > 0
        
        logging.info("No existing cache entries found to invalidate")
        return True
    except Exception:
        logging.error("An error occurred while invalidating multiple cache keys", exc_info=True)
        return False