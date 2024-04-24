from typing import Any
from uuid import UUID

from pydantic import BaseModel

from matter_persistence.redis.async_redis_client import AsyncRedisClient, get_connection_pool
from matter_persistence.redis.cache_helper import CacheHelper
from matter_persistence.redis.exceptions import (
    CacheRecordNotFoundError,
    CacheRecordNotSavedError,
)
from matter_persistence.redis.utils import compress_pickle_data, decompress_pickle_data


class APICacheClient:
    """
    APICacheClient class is responsible for interacting with a cache client to save, retrieve, delete, and check the existence of cache records.

    Methods:
    - __get_cache_client: Private method to get the cache client.
    - save_raw: Saves a raw value to the cache with an optional expiration time.
    - find_raw: Retrieves a raw value from the cache.
    - delete_raw: Deletes a raw value from the cache.
    - raw_cache_record_exists: Checks if a raw cache record exists.
    - cache_record_exists: Checks if a cache record exists.
    - save_object: Saves an object to the cache with an optional expiration time. The object is serialized and compressed before storing.
    - find_object: Retrieves an object from the cache and returns it as a CacheRecordModel instance.
    - save_cache_record: Same as save_object method.
    - find_cache_record: Same as find_object method.
    - is_cache_alive: Checks if the cache client is alive.

    Usage example:
    cache_client = APICacheClient()
    await cache_client.save_raw("key", "value", expiration_in_seconds=60)
    value = await cache_client.find_raw("key")
    await cache_client.delete_raw("key")
    exists = await cache_client.raw_cache_record_exists("key")
    exists = await cache_client.cache_record_exists(organization_id, internal_id, object_class)
    await cache_client.save_object(organization_id, internal_id, value)
    cache_record = await cache_client.find_object(organization_id, internal_id, object_class)
    await cache_client.save_cache_record(organization_id, internal_id, value)
    cache_record = await cache_client.find_cache_record(organization_id, internal_id, object_class)
    is_alive = await cache_client.is_cache_alive()
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

    async def save_raw(
        self,
        key: str,
        value: Any,
        object_class: type[BaseModel] | None = None,
        expiration_in_seconds: int | None = None,
    ):
        object_name = object_class.__name__ if object_class else None
        hash_key = CacheHelper.create_basic_hash_key(key, object_name)
        if object_class:
            value = value.model_dump_json()

        async with self.__get_cache_client() as cache_client:
            if expiration_in_seconds:
                result = await cache_client.set_value(hash_key, value, ttl=expiration_in_seconds)
            else:
                result = await cache_client.set_value(hash_key, value)

        if not result:
            raise CacheRecordNotSavedError(
                description=f"Unable to store value in cache. Key: {key}",
                detail={"key": key, "hash_key": hash_key},
            )

        return result

    async def find_raw(self, key: str, object_class: type[BaseModel] | None = None) -> Any:
        object_name = object_class.__name__ if object_class else None
        hash_key = CacheHelper.create_basic_hash_key(key, object_name)
        async with self.__get_cache_client() as cache_client:
            value = await cache_client.get_value(hash_key)
        if not value:
            raise CacheRecordNotFoundError(
                description=f"Unable to retrieve value from cache. Key: {key}",
                detail={"key": key, "hash_key": hash_key},
            )

        if object_class:
            if isinstance(value, list):
                value = [object_class.parse_raw(item) for item in value]
            else:
                value = object_class.model_validate_json(value)

        return value

    async def delete_raw(
        self,
        key: str,
        object_class: type[BaseModel] | None = None,
    ) -> Any:
        object_name = object_class.__name__ if object_class else None
        hash_key = CacheHelper.create_basic_hash_key(key, object_name)

        async with self.__get_cache_client() as cache_client:
            if not await cache_client.delete_key(hash_key):
                raise CacheRecordNotFoundError(
                    description=f"Unable to retrieve value from cache. Key: {key}",
                    detail={"key": key, "hash_key": hash_key},
                )

    async def raw_cache_record_exists(
        self,
        key: str,
        object_class: object | None = None,
    ):
        object_name = object_class.__name__ if object_class else None
        hash_key = CacheHelper.create_basic_hash_key(key, object_name)
        async with self.__get_cache_client() as cache_client:
            return await cache_client.exists(hash_key)

    async def cache_record_exists(
        self,
        organization_id: UUID,
        internal_id: int | str | UUID,
        object_class: object,
    ):
        key = CacheHelper.create_hash_key(
            organization_id=organization_id,
            internal_id=str(internal_id),
            object_class=object_class,
        )
        async with self.__get_cache_client() as cache_client:
            return await cache_client.exists(key)

    async def save_object(
        self,
        organization_id: UUID,
        internal_id: int | str | UUID,
        value: Any,
        object_class: object | None = None,
        expiration_in_seconds: int | None = None,
    ):
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
                    compress_pickle_data(cache_record),
                    ttl=expiration_in_seconds,
                )
            else:
                result = await cache_client.set_value(cache_record.hash_key, compress_pickle_data(cache_record))

        if not result:
            raise CacheRecordNotSavedError(
                description=f"Unable to store Cache Record {cache_record.hash_key}",
                detail=cache_record,
            )

    async def find_object(
        self,
        organization_id: UUID,
        internal_id: int | str | UUID,
        object_class: object,
    ):
        key = CacheHelper.create_hash_key(
            organization_id=organization_id,
            internal_id=str(internal_id),
            object_class=object_class,
        )
        async with self.__get_cache_client() as cache_client:
            raw_cache_record = await cache_client.get_value(key)

        if not raw_cache_record:
            raise CacheRecordNotFoundError(
                description=f"Unable to find Cache Record with the key: {key}",
                detail=raw_cache_record,
            )

        return decompress_pickle_data(raw_cache_record)

    async def save_cache_record(
        self,
        organization_id: UUID,
        internal_id: int | str | UUID,
        value: Any,
        object_class: type[BaseModel] | None = None,
        expiration_in_seconds: int | None = None,
    ):
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
                    compress_pickle_data(cache_record),
                    ttl=expiration_in_seconds,
                )
            else:
                result = await cache_client.set_value(cache_record.hash_key, compress_pickle_data(cache_record))

        if not result:
            raise CacheRecordNotSavedError(
                description=f"Unable to store Cache Record {cache_record.hash_key}",
                detail=cache_record,
            )

    async def find_cache_record(
        self,
        organization_id: UUID,
        internal_id: int | str | UUID,
        object_class: type[BaseModel],
    ):
        key = CacheHelper.create_hash_key(
            organization_id=organization_id,
            internal_id=str(internal_id),
            object_class=object_class,
        )
        async with self.__get_cache_client() as cache_client:
            raw_cache_record = await cache_client.get_value(key)

        if not raw_cache_record:
            raise CacheRecordNotFoundError(
                description=f"Unable to find Cache Record with the key: {key}",
                detail=raw_cache_record,
            )

        return decompress_pickle_data(raw_cache_record)

    async def is_cache_alive(self):
        async with self.__get_cache_client() as cache_client:
            return await cache_client.is_alive()
