from typing import Any

from aiocache import Cache

from .config import CacheConfig, CacheEngine


class CacheClient:
    __cache_engine = None
    __default_expiration_time = 30

    @classmethod
    def start(cls, cache_config: CacheConfig):
        if cls.__cache_engine is not None:
            return

        engine = cache_config.engine

        if engine == CacheEngine.MEMORY:
            cls.__cache_engine = Cache()
        elif engine == CacheEngine.MEMCACHED:  # pragma: no cover
            cls.__cache_engine = Cache(Cache.MEMCACHED, endpoint=cache_config.endpoint, port=cache_config.port)

        cls.__default_expiration_time = cache_config.object_expiration_time

    @classmethod
    def get_engine(cls):
        return cls.__cache_engine

    @classmethod
    async def clear(cls):
        await cls.__cache_engine.clear()

    @classmethod
    def get_default_object_expiration(cls):
        return cls.__default_expiration_time


async def cache_get(key: str) -> Any:
    return await CacheClient.get_engine().get(key)


async def cache_set(key: str, value: Any, expire_in: int = None):
    if expire_in is None:
        expire_in = CacheClient.get_default_object_expiration()
    await CacheClient.get_engine().set(key, value, ttl=expire_in)


async def cache_delete(key: str):
    await CacheClient.get_engine().delete(key)
