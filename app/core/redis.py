import redis

from app.core.config import settings

redis_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    protocol=2,  # RESP2 works with every Redis version; redis-py 8 defaults to RESP3
    # The cache is optional, so fail fast rather than stall requests when Redis is down.
    socket_connect_timeout=0.5,
    socket_timeout=0.5,
)
