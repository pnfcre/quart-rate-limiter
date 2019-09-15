from datetime import datetime
from typing import Any, Optional

from aioredis import create_redis, Redis

from .store import RateLimiterStoreABC


class RedisStore(RateLimiterStoreABC):
    """An redis backed store of rate limits.

    Arguments:
        address: The address of the redis instance.
        kwargs: Any keyword arguments to pass to the redis client on
            creation, see the aioredis documentation.
    """

    def __init__(self, address: str, **kwargs: Any) -> None:
        self._redis: Optional[Redis] = None
        self._redis_arguments = (address, kwargs)

    async def before_serving(self) -> None:
        self._redis = await create_redis(self._redis_arguments[0], **self._redis_arguments[1])

    async def get(self, key: str, default: datetime) -> datetime:
        result = await self._redis.get(key)
        if result is None:
            return default
        else:
            return result

    async def set(self, key: str, tat: datetime) -> None:
        await self._redis.set(key, tat)

    async def after_serving(self) -> None:
        self._redis.close()
        await self._redis.wait_closed()
        self._redis = None
