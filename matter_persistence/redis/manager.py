from uuid import UUID

from orjson import loads

from matter_persistence.redis.async_redis_client import AsyncRedisClient, get_connection_pool
from matter_persistence.redis.base import CacheRecordModel, Model
from matter_persistence.redis.cache_helper import CacheHelper
from matter_persistence.redis.exceptions import (
    CacheRecordNotFoundError,
    CacheRecordNotSavedError,
)


class CacheManager:
    """
    CacheManager class is responsible for interacting with a cache client to save, retrieve, delete,
    and check the existence of cache records.

    Methods:
    - __get_cache_client: Private method to get the cache client.
    - save_value: Saves a value to the cache with an optional expiration time.
    - get_value: Retrieves a value from the cache.
    - delete_value: Deletes a value from the cache.
    - cache_record_exists: Checks if a cache record exists.
    - is_cache_alive: Checks if the cache client is alive.

    Usage example:
        Check examples/redis.ipynb for usage examples.
    """

    def __init__(self, host: str, port: int, db: int = 0):
        self.__connection_pool = get_connection_pool(
            host=host,
            port=port,
            db=db,
        )

    def __get_cache_client(self) -> AsyncRedisClient:
        return AsyncRedisClient(connection_pool=self.__connection_pool)

    async def close_connection_pool(self) -> None:
        """
        Closes the singleton connection pool to Redis.

        Since the connection pool is a singleton, this effectively stops the application process from being able
        to connect to Redis, so use only once, when all connections should be closed!
        """
        await self.__connection_pool.aclose()

    async def save_value(
        self,
        organization_id: UUID,
        internal_id: int | str | UUID,
        value: type[Model],
        object_class: type[Model] | None = None,
        expiration_in_seconds: int | None = None,
        **kwargs,  # they are passed to cache_record.model_dump_json()
    ):
        """
        Saves value to the cache with an optional expiration time.
        """
        cache_record = CacheHelper.create_cache_record(
            organization_id=organization_id,
            internal_id=str(internal_id),
            value=value,
            object_class=object_class,
            expiration_in_seconds=expiration_in_seconds,
        )
        async with self.__get_cache_client() as cache_client:
            if expiration_in_seconds:
                result = await cache_client.set_value(
                    cache_record.hash_key,
                    cache_record.model_dump_json(**kwargs),
                    ttl=expiration_in_seconds,
                )
            else:
                result = await cache_client.set_value(cache_record.hash_key, cache_record.model_dump_json(**kwargs))

        if not result:
            raise CacheRecordNotSavedError(
                description=f"Unable to store Cache Record {cache_record.hash_key}",
                detail=cache_record,
            )

    async def get_value(
        self,
        organization_id: UUID,
        internal_id: int | str | UUID,
        object_class: type[Model] | None = None,
        **kwargs,  # they are passed to CacheRecordModel.model_validate_json()
    ):
        """
        Gets a value from the cache.
        """
        key = CacheHelper.create_hash_key(
            organization_id=organization_id,
            internal_id=str(internal_id),
            object_class=object_class,
        )
        async with self.__get_cache_client() as cache_client:
            cache_record_json = await cache_client.get_value(key)

        if not cache_record_json:
            raise CacheRecordNotFoundError(
                description=f"Unable to find Cache Record with the key: {key}",
                detail=cache_record_json,
            )

        return CacheRecordModel.model_validate(loads(cache_record_json))

    async def delete_value(
        self,
        organization_id: UUID,
        internal_id: int | str | UUID,
        object_class: type[Model] | None = None,
    ):
        """
        Deletes a value from the cache.
        """
        key = CacheHelper.create_hash_key(
            organization_id=organization_id,
            internal_id=str(internal_id),
            object_class=object_class,
        )

        async with self.__get_cache_client() as cache_client:
            if not await cache_client.delete_key(key):
                raise CacheRecordNotFoundError(
                    description=f"Unable to retrieve value from cache. Key: {key}",
                    detail={"key": key},
                )

    async def cache_record_exists(
        self,
        organization_id: UUID,
        internal_id: int | str | UUID,
        object_class: type[Model] | None = None,
    ):
        """
        Checks if a cache record exists.
        """
        key = CacheHelper.create_hash_key(
            organization_id=organization_id,
            internal_id=str(internal_id),
            object_class=object_class,
        )
        async with self.__get_cache_client() as cache_client:
            return bool(await cache_client.exists(key))  # cache_client.exists() returns 0 or 1

    async def is_cache_alive(self):
        """
        Checks if the cache client is alive.
        """
        async with self.__get_cache_client() as cache_client:
            return await cache_client.is_alive()
