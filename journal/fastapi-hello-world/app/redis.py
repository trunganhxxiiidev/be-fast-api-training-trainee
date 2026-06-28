from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis, from_url

from app.config import get_settings

_redis: Redis | None = None


async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        settings = get_settings()
        _redis = from_url(settings.redis_url, decode_responses=True)
    return _redis


RedisDep = Annotated[Redis, Depends(get_redis)]
