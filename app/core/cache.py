import json
from typing import Any
from app.core.redis import redis_client

CACHE_TTL_SECONDS = 60


def make_list_cache_key(resource: str, page: int, size: int, company: str | None = None) -> str:
    key = f"{resource}:{page}:{size}"
    if company:
        normalized_company = company.strip().lower().replace(" ", "_")
        key = f"{key}:company:{normalized_company}"
    return key


def get_cached_resource(key: str) -> Any:
    cached = redis_client.get(key)
    return json.loads(cached) if cached else None


def set_cached_resource(key: str, data: Any, ttl: int = CACHE_TTL_SECONDS) -> None:
    redis_client.setex(key, ttl, json.dumps(data))


def invalidate_list_cache(resource: str) -> None:
    keys = list(redis_client.scan_iter(f"{resource}:*"))
    if keys:
        redis_client.delete(*keys)
