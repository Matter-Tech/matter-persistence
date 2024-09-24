from collections.abc import Sequence
from typing import Any
from uuid import UUID

from pydantic import TypeAdapter, ValidationError
from redis import asyncio as aioredis

from matter_persistence.redis.async_redis_client import AsyncRedisClient
from matter_persistence.redis.base import Model
from matter_persistence.redis.cache_helper import CacheHelper
from matter_persistence.redis.exceptions import (
    CacheRecordNotFoundError,
    CacheRecordNotSavedError,
)
from matter_persistence.redis.utils import compress_pickle_data, decompress_pickle_data, validate_connection_arguments


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
    - save_with_key: Saves a value to the cache with an optional expiration time using a key.
    - get_with_key: Retrieves a value from the cache using a key.
    - delete_with_key: Deletes a value from the cache using a key.
    - is_cache_alive: Checks if the cache client is alive.

    Usage example:
        Check examples/redis.ipynb for usage examples.
    """

    def __init__(
        self,
        connection: aioredis.Redis | None = None,
        connection_pool: aioredis.ConnectionPool | None = None,
        sentinel: aioredis.Sentinel | None = None,
        sentinel_service_name: str | None = None,
    ):
        validate_connection_arguments(connection, connection_pool, sentinel)
        self.__connection = connection
        self.__connection_pool = connection_pool
        self.__sentinel = sentinel
        self.__sentinel_service_name = sentinel_service_name

    def __get_cache_client(self, for_writing: bool = False) -> AsyncRedisClient:
        return AsyncRedisClient(
            connection=self.__connection,
            connection_pool=self.__connection_pool,
            sentinel=self.__sentinel,
            sentinel_service_name=self.__sentinel_service_name,
            for_writing=for_writing,
        )

    async def close_connection_pool(self) -> None:
        """
        Closes the singleton connection pool to Redis.

        Since the connection pool is a singleton, this effectively stops the application process from being able
        to connect to Redis, so use only once, when all connections should be closed!
        """
        if self.__connection_pool:
            await self.__connection_pool.aclose()
            # from redis: By default, let Redis. auto_close_connection_pool decide whether to close the connection pool.
            # therefore not calling "await self.__connection.aclose()"
        if self.__sentinel:
            for sentinel_connection in self.__sentinel.sentinels:
                await sentinel_connection.aclose()

    async def save_value(
        self,
        organization_id: UUID,
        internal_id: int | str | UUID,
        value: Any,
        object_class: type[Model] | None = None,
        expiration_in_seconds: int | None = None,
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
        async with self.__get_cache_client(for_writing=True) as cache_client:
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

    async def get_value(
        self,
        organization_id: UUID,
        internal_id: int | str | UUID,
        object_class: type[Model] | None = None,
    ):
        """
        Gets a value from the cache.
        """
        key = CacheHelper.create_hash_key(
            organization_id=organization_id,
            internal_id=str(internal_id),
            object_class=object_class,
        )
        async with self.__get_cache_client(for_writing=False) as cache_client:
            compressed_pickled_cache_record = await cache_client.get_value(key)

        if not compressed_pickled_cache_record:
            raise CacheRecordNotFoundError(
                description=f"Unable to find Cache Record with the key: {key}",
                detail=compressed_pickled_cache_record,
            )

        return decompress_pickle_data(compressed_pickled_cache_record)

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

        async with self.__get_cache_client(for_writing=True) as cache_client:
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
        async with self.__get_cache_client(for_writing=False) as cache_client:
            return bool(await cache_client.exists(key))  # cache_client.exists() returns 0 or 1

    async def save_with_key(
        self,
        key: str,
        value: Any,
        object_class: type[Model] | None = None,
        expiration_in_seconds: int | None = None,
        use_key_as_is: bool = False,
    ):
        hash_key = self._get_key_from_params(key=key, object_class=object_class, use_key_as_is=use_key_as_is)
        if object_class:
            value = value.model_dump_json()

        async with self.__get_cache_client(for_writing=True) as cache_client:
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

    async def save_many_with_keys(
        self,
        values_to_store: dict[str, Any],
        object_class: type[Model] | None = None,
        expiration_in_seconds: int | None = None,
    ) -> None:
        """
        Saves many given keys with values.

        Note that values might be sequences of objects of given object_class, but they will be
        stored as lists dumped as JSONs in Redis.

        :param values_to_store: a dictionary, mapping keys to values (see note above)
        :param object_class: optional model to facilitate serialisation of data
        :param expiration_in_seconds: cache expiration time in seconds
        """
        object_name = object_class.__name__ if object_class else None

        async with self.__get_cache_client(for_writing=True) as cache_client:
            if object_class is not None:
                processed_input = {}
                for key, value in values_to_store.items():
                    processed_key = CacheHelper.create_basic_hash_key(key, object_name)
                    if isinstance(value, Sequence):
                        adapter = TypeAdapter(list[object_class])  # type: ignore[valid-type]
                        if not isinstance(value, list):
                            pre_processed_value = [v for v in value]
                        else:
                            pre_processed_value = value
                        processed_value = adapter.dump_json(pre_processed_value)
                    else:
                        processed_value = value.model_dump_json()
                    processed_input[processed_key] = processed_value
            else:
                processed_input = {
                    CacheHelper.create_basic_hash_key(key, object_name): value for key, value in values_to_store.items()
                }
            await cache_client.set_many_values(processed_input, ttl=expiration_in_seconds)

    async def get_with_key(self, key: str, object_class: type[Model] | None = None, use_key_as_is: bool = False) -> Any:
        hash_key = self._get_key_from_params(key=key, object_class=object_class, use_key_as_is=use_key_as_is)
        async with self.__get_cache_client(for_writing=False) as cache_client:
            value = await cache_client.get_value(hash_key)
        if not value:
            raise CacheRecordNotFoundError(
                description=f"Unable to retrieve value from cache. Key: {key}",
                detail={"key": key, "hash_key": hash_key},
            )

        if object_class:
            if isinstance(value, list):
                value = [object_class.model_validate_json(item) for item in value]
            else:
                value = object_class.model_validate_json(value)

        return value

    async def get_many_with_keys(
        self, keys: Sequence[str], object_class: type[Model] | None = None
    ) -> dict[str, bytes | Model | list[Model] | None]:
        """
        Gets multiple values from the cache.

        If object_class is specified, tries to deserialise the values into the given class. A list of values in the cache
        for a single key is also supported. Values for all keys need to be of the same class.

        The resulting dictionary values can contain:
        - an object or a list of objects (if object_class is given)
        - a raw bytes value (if object_class isn't given)
        - None, if the key doesn't exist in cache

        :param keys: which keys to get from the cache
        :param object_class: used in deserialisation of cached values
        :return: a dictionary, mapping the original set of keys to the corresponding values from the cache
        """
        object_name = object_class.__name__ if object_class else None
        return_set: dict[str, bytes | Model | list[Model] | None] = {}
        async with self.__get_cache_client(for_writing=False) as cache_client:
            processed_input = {
                CacheHelper.create_basic_hash_key(original_key, object_name): original_key for original_key in keys
            }
            response: dict[str, bytes] = await cache_client.get_many_values(processed_input.keys())
            if object_class:
                for key, value in response.items():
                    if value is not None:
                        try:
                            return_set[processed_input[key]] = object_class.model_validate_json(value)
                        except ValidationError:
                            adapter = TypeAdapter(list[object_class])  # type: ignore[valid-type]
                            return_set[processed_input[key]] = adapter.validate_json(value)
                    else:
                        return_set[processed_input[key]] = value
            else:
                return_set = {processed_input[key]: value for key, value in response.items()}
        return return_set

    async def delete_with_key(
        self,
        key: str,
        object_class: type[Model] | None = None,
        use_key_as_is: bool = False,
    ) -> Any:
        hash_key = self._get_key_from_params(key=key, object_class=object_class, use_key_as_is=use_key_as_is)
        async with self.__get_cache_client(for_writing=True) as cache_client:
            if not await cache_client.delete_key(hash_key):
                raise CacheRecordNotFoundError(
                    description=f"Unable to retrieve value from cache. Key: {key}",
                    detail={"key": key, "hash_key": hash_key},
                )

    async def cache_record_with_key_exists(
        self,
        key: str,
        object_class: type[Model] | None = None,
        use_key_as_is: bool = False,
    ) -> bool:
        hash_key = self._get_key_from_params(key=key, object_class=object_class, use_key_as_is=use_key_as_is)
        async with self.__get_cache_client(for_writing=False) as cache_client:
            return bool(await cache_client.exists(hash_key))  # cache_client.exists() returns 0 or 1

    async def is_cache_alive(self):
        """
        Checks if the cache client is alive.
        """
        async with self.__get_cache_client(for_writing=False) as cache_client:
            return await cache_client.is_alive()

    @staticmethod
    def _get_key_from_params(key: str, object_class: type[Model] | None = None, use_key_as_is: bool = False) -> str:
        if use_key_as_is:
            return key
        else:
            object_name = object_class.__name__ if object_class else None
            return CacheHelper.create_basic_hash_key(key, object_name)
