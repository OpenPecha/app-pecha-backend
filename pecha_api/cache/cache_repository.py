import json
from typing import Any, Optional

from redis import Redis

from pecha_api import config

from pydantic.json import pydantic_encoder


_client: Optional[Redis] = None


def get_client() -> Redis:
    """Get or create Redis client instance"""
    global _client
    if _client is None:
        _client = Redis(
            host=config.get("CACHE_HOST"),
            port=config.get_int("CACHE_PORT"),
            db=config.get_int("CACHE_DB"),
            decode_responses=True
        )
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
        return client.setex(full_key, timeout, value)
    except Exception:
        import logging
        logging.error("An error occurred in set_cache", exc_info=True)

        return False


async def get_cache_data(hash_key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        value = client.get(full_key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    except Exception:
        return None


async def delete_cache(hash_key: str) -> bool:
    """Delete key from cache"""
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        return bool(client.delete(full_key))
    except Exception:
        return False


async def exists_in_cache(hash_key: str) -> bool:
    """Check if key exists in cache"""
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        return bool(client.exists(full_key))
    except Exception:
        return False


async def clear_cache(pattern: str = "*") -> bool:
    """Clear all keys matching pattern"""
    try:
        client = get_client()
        full_key = _build_key(pattern)
        keys = client.keys(full_key)
        if keys:
            return bool(client.delete(*keys))
        return True
    except Exception:
        return False