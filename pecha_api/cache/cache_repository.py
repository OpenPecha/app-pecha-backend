import json
from typing import Any, Optional

from redis import Redis

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


def set_cache(hash_key: str, value: Any) -> bool:
    """Set value in cache with default timeout"""
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        timeout = config.get_int("CACHE_DEFAULT_TIMEOUT")
        if not isinstance(value, (str, bytes)):
            value = json.dumps(value, default=pydantic_encoder)
        return bool(client.setex(full_key, timeout, value))
    except Exception:
        logging.error("An error occurred in set_cache", exc_info=True)
        return False

def get_cache_data(hash_key: str) -> Optional[Any]:
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
            logging.error("Failed to decode JSON from cache", exc_info=True)
            return value
    except Exception:
        logging.error("An error occurred in get_cache_data", exc_info=True)
        return None


def delete_cache(hash_key: str) -> bool:
    """Delete key from cache"""
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        return bool(client.delete(full_key))
    except Exception:
        logging.error("An error occurred in delete_cache", exc_info=True)
        return False


def exists_in_cache(hash_key: str) -> bool:
    """Check if key exists in cache"""
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        return bool(client.exists(full_key))
    except Exception:
        logging.error("An error occurred in exists_in_cache", exc_info=True)
        return False


def clear_cache(pattern: str = "*") -> bool:
    """Clear all keys matching pattern"""
    try:
        client = get_client()
        full_key = _build_key(pattern)
        keys = client.keys(full_key)
        if keys:
            return bool(client.delete(*keys))
        return True
    except Exception:
        logging.error("An error occurred in clear_cache", exc_info=True)
        return False