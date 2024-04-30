from datetime import timedelta

from redis import asyncio as aioredis

from matter_persistence.decorators import retry_if_failed


class AsyncRedisClient:
    """
    Class representing an asynchronous Redis client.

    Arguments:
        connection_pool (ConnectionPool): The Redis connection pool to use for establishing a connection with.

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
        self, connection: aioredis.Redis | None = None, connection_pool: aioredis.ConnectionPool | None = None
    ):
        if (connection and connection_pool is None) or (connection is None and connection_pool):
            self.connection = connection
            self._connection_pool = connection_pool
        else:
            raise ValueError(
                "Invalid argument combination. Please provide either: "
                "connection: aioredis.Redis and connection_pool: None, OR "
                "connection: None and connection_pool: aioredis.ConnectionPool"
            )

    async def __aenter__(self):
        if self._connection_pool:
            await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def connect(self):
        if self._connection_pool:
            self.connection = await aioredis.Redis(connection_pool=self._connection_pool)

    async def close(self):
        if self.connection:
            await self.connection.aclose()
        if self._connection_pool:
            await self._connection_pool.aclose()

    @retry_if_failed
    async def set_value(self, key: str, value: str, ttl=None):
        result = await self.connection.set(key, value)  # type: ignore
        if ttl is not None:
            await self.connection.expire(key, ttl)  # type: ignore

        return result

    @retry_if_failed
    async def get_value(self, key: str):
        return await self.connection.get(key)  # type: ignore

    @retry_if_failed
    async def set_hash_field(self, hash_key: str, field: str, value: str, ttl: int | timedelta | None = None):
        result = await self.connection.hset(hash_key, field, value)  # type: ignore
        if ttl is not None:
            await self.connection.expire(hash_key, ttl)  # type: ignore

        return result

    @retry_if_failed
    async def get_hash_field(self, hash_key: str, field: str):
        return await self.connection.hget(hash_key, field)  # type: ignore

    @retry_if_failed
    async def get_all_hash_fields(self, hash_key: str):
        return await self.connection.hgetall(hash_key)  # type: ignore

    @retry_if_failed
    async def delete_key(self, key: str):
        return await self.connection.delete(key)  # type: ignore

    @retry_if_failed
    async def exists(self, key_or_hash: str, field: str | None = None):
        if field is None:
            return await self.connection.exists(key_or_hash)  # type: ignore
        else:
            return await self.connection.hexists(key_or_hash, field)  # type: ignore

    @retry_if_failed
    async def is_alive(self):
        return await self.connection.ping()
