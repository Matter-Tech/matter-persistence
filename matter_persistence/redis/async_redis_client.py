import contextlib
from collections.abc import AsyncIterator, Mapping, Sequence
from datetime import timedelta

from redis import asyncio as aioredis

from matter_persistence.decorators import retry_if_failed
from matter_persistence.redis.exceptions import CacheConnectionNotEstablishedError
from matter_persistence.redis.utils import validate_connection_arguments


class AsyncRedisClient:
    """
    Class representing an asynchronous Redis client.

    Arguments:
        connection_pool (ConnectionPool): The Redis connection pool to use for establishing a connection with.
        connection (Redis): The Redis connection to use; connections will not be pooled - only this one will be used.
        sentinel (Sentinel): The Redis Sentinel to use. Provides option of using the client either for reading or writing.

    Methods:
        async def __aenter__(self) -> AsyncRedisClient:
            Context manager enter method. Establishes a connection to the Redis server.

        async def __aexit__(self, exc_type, exc_value, traceback) -> None:
            Context manager exit method. Closes the connection to the Redis server.

        async def connect(self) -> None:
            Establishes a connection to the Redis server.

        async def close(self) -> None:
            Closes the connection to the Redis server.

        async def set_value(self, key: str, value: Union[str, bytes], ttl: Optional[int] = None) -> Optional[str]:
            Sets the value of a key in Redis. If ttl is provided, sets the expiration time in seconds.

        async def get_value(self, key: str) -> Optional[str]:
            Retrieves the value of a key from Redis.

        async def set_hash_field(self, hash_key: str, field: Union[str, bytes], value: Union[str, bytes], ttl: Optional[int] = None) -> Optional[int]:
            Sets the value of a field in a Redis hash. If ttl is provided, sets the expiration time in seconds.

        async def get_hash_field(self, hash_key: str, field: Union[str, bytes]) -> Optional[bytes]:
            Retrieves the value of a field from a Redis hash.

        async def get_all_hash_fields(self, hash_key: str) -> Optional[Dict[Union[str, bytes], Union[str, bytes]]]:
            Retrieves all fields and values from a Redis hash.

        async def delete_key(self, key: str) -> Optional[int]:
            Deletes a key from Redis.

        async def exists(self, key_or_hash: str, field: Optional[Union[str, bytes]] = None) -> bool:
            Checks if a key or field exists in Redis.

        async def is_alive(self) -> str:
            Checks if the Redis server is alive by sending a ping command.
    """

    def __init__(
        self,
        connection: aioredis.Redis | None = None,
        connection_pool: aioredis.ConnectionPool | None = None,
        sentinel: aioredis.Sentinel | None = None,
        sentinel_service_name: str | None = None,
        for_writing: bool = False,
    ):
        validate_connection_arguments(connection, connection_pool, sentinel)
        self.connection = connection
        self._connection_pool = connection_pool
        self._sentinel = sentinel
        self._sentinel_service_name = sentinel_service_name
        self._for_writing = for_writing

    async def __aenter__(self):
        if self._connection_pool:
            self.connection = await aioredis.Redis(connection_pool=self._connection_pool)
        elif self._sentinel:
            if self._for_writing:
                self.connection = await self._sentinel.master_for(service_name=self._sentinel_service_name)
            else:
                self.connection = await self._sentinel.slave_for(service_name=self._sentinel_service_name)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.connection:
            await self.connection.aclose()

    @contextlib.asynccontextmanager
    async def pipeline(
        self,
        transaction: bool = True,
    ) -> AsyncIterator[aioredis.client.Pipeline]:
        if not isinstance(self.connection, aioredis.Redis):
            raise CacheConnectionNotEstablishedError(
                "You cannot use the client if the connection isn't established. Use as async context manager."
            )
        async with self.connection.pipeline(transaction=transaction) as pipe:
            yield pipe

    @retry_if_failed
    async def set_value(self, key: str, value: str, ttl=None):
        result = await self.connection.set(key, value)  # type: ignore
        if ttl is not None:
            await self.connection.expire(key, ttl)  # type: ignore

        return result

    @retry_if_failed
    async def set_many_values(self, values: Mapping[str, str], ttl: int | None = None) -> None:
        async with self.pipeline() as pipe:
            await pipe.mset(values)
            if ttl is not None:
                for key in values.keys():
                    await pipe.expire(key, ttl)
            await pipe.execute()

    @retry_if_failed
    async def get_value(self, key: str) -> bytes:
        return await self.connection.get(key)  # type: ignore

    @retry_if_failed
    async def get_many_values(self, keys: Sequence[str]) -> dict[str, bytes]:
        if not isinstance(self.connection, aioredis.Redis):
            raise CacheConnectionNotEstablishedError(
                "You cannot use the client if the connection isn't established. Use as async context manager."
            )
        response = await self.connection.mget(keys)
        return dict(zip(keys, response, strict=True))

    @retry_if_failed
    async def set_hash_field(self, hash_key: str, field: str, value: str, ttl: int | timedelta | None = None):
        result = await self.connection.hset(hash_key, field, value)  # type: ignore
        if ttl is not None:
            await self.connection.expire(hash_key, ttl)  # type: ignore

        return result

    @retry_if_failed
    async def get_hash_field(self, hash_key: str, field: str) -> bytes:
        return await self.connection.hget(hash_key, field)  # type: ignore

    @retry_if_failed
    async def get_all_hash_fields(self, hash_key: str) -> list[bytes]:
        return await self.connection.hgetall(hash_key)  # type: ignore

    @retry_if_failed
    async def delete_key(self, key: str):
        return await self.connection.delete(key)  # type: ignore

    @retry_if_failed
    async def exists(self, key_or_hash: str, field: str | None = None) -> int:
        if field is None:
            return await self.connection.exists(key_or_hash)  # type: ignore
        else:
            return await self.connection.hexists(key_or_hash, field)  # type: ignore

    @retry_if_failed
    async def exists_many(self, keys: Sequence[str]) -> bool:
        if not isinstance(self.connection, aioredis.Redis):
            raise CacheConnectionNotEstablishedError(
                "You cannot use the client if the connection isn't established. Use as async context manager."
            )
        number_of_existing_keys: int = await self.connection.exists(*keys)
        return number_of_existing_keys == len(keys)

    @retry_if_failed
    async def is_alive(self):
        return await self.connection.ping()
