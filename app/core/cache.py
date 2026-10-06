"""Read-through cache helpers.

The cache is an optimisation, never a dependency: if Redis is down, every
helper logs a warning and the request falls through to MongoDB.
"""

import json
import logging
from typing import Any

import redis

from app.core import redis as redis_module
from app.core.config import settings

logger = logging.getLogger(__name__)


def make_list_cache_key(resource: str, page: int, size: int, **filters: str | None) -> str:
    key = f"{resource}:list:{page}:{size}"
    for name, value in sorted(filters.items()):
        if value:
            key += f":{name}:{value.strip().lower().replace(' ', '_')}"
    return key


def make_item_cache_key(resource: str, item_id: Any) -> str:
    return f"{resource}:item:{item_id}"


def get_cached(key: str) -> Any:
    try:
        cached = redis_module.redis_client.get(key)
    except redis.RedisError as exc:
        logger.warning("Cache read failed for %s: %s", key, exc)
        return None
    return json.loads(cached) if cached else None


def set_cached(key: str, data: Any, ttl: int | None = None) -> None:
    try:
        redis_module.redis_client.set(key, json.dumps(data), ex=ttl or settings.cache_ttl_seconds)
    except redis.RedisError as exc:
        logger.warning("Cache write failed for %s: %s", key, exc)


def invalidate(resource: str, item_id: Any | None = None) -> None:
    """Drop every cached list page for `resource`, plus one item if given."""
    try:
        client = redis_module.redis_client
        keys = list(client.scan_iter(f"{resource}:list:*"))
        if item_id is not None:
            keys.append(make_item_cache_key(resource, item_id))
        if keys:
            client.delete(*keys)
    except redis.RedisError as exc:
        logger.warning("Cache invalidation failed for %s: %s", resource, exc)
