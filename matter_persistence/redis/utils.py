import gzip
import itertools
import pickle
from functools import lru_cache
from typing import Any

from redis import asyncio as aioredis


@lru_cache(maxsize=1)
def get_connection_pool(
    host: str, port: int, db: int = 0, username: str = "default", password: str | None = None
) -> aioredis.ConnectionPool:
    """
    Gets a connection pool to Redis. Note that it's a singleton - an application process should always only
    create 1 connection pool & reuse it for all internal connections.

    Args:
        host (str): Redis host
        port (int): Redis port
        db (int): Redis logical database, normally only 0 is used
        username (str): Redis username, defaults to "default", as mentioned in https://redis.io/docs/latest/commands/auth/
        password (str): Redis password, optional

    Returns:
        connection_pool (aioredis.ConnectionPool): a connection pool to be reused by connections
            established in the application
    """
    redis_url = f"redis://{host}:{port}/{db}"
    if password is not None:
        redis_url = redis_url.replace("://", f"://{username}:{password}@")
    return aioredis.ConnectionPool.from_url(redis_url)


async def get_sentinel(
    sentinel_addresses: list[tuple[str, int]], password: str | None = None, **kwargs: Any
) -> aioredis.Sentinel:
    """
    Gets a Sentinel instance for connecting to a set of Redis nodes connected using the sentinel protocol.

    Read more about the Redis Sentinel protocol here: https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/

    Args:
        sentinel_addresses (list[tuple[str, int]]): list of addresses pointing to sentinel endpoints in the Redis nodes;
            or an address of a Kubernetes service exposing sentinel capabilities
        password (str): Redis password, optional; will also be used for sentinels
        kwargs (Any): keyword arguments passed to redis.asyncio.sentinel.Sentinel & then to underlying
            redis.asyncio.Redis connections

    Returns:
        sentinel (redis.asyncio.sentinel.Sentinel): a Sentinel instance
    """
    if password is not None:
        kwargs["password"] = password
        kwargs["sentinel_kwargs"] = {**kwargs.get("sentinel_kwargs", dict()), **dict(password=password)}
    sentinel = aioredis.Sentinel(sentinel_addresses, **kwargs)
    return sentinel


def compress_pickle_data(data: Any) -> bytes:
    pickled_data = pickle.dumps(data)  # Serialize the data into bytes using pickle
    compressed_data = gzip.compress(pickled_data)  # Compress the pickled data using gzip
    return compressed_data


def decompress_pickle_data(compressed_data: bytes) -> Any:
    decompressed_data = gzip.decompress(compressed_data)  # Decompress the compressed data using gzip
    data = pickle.loads(decompressed_data)  # Deserialize the data back into Python objects using pickle
    return data


def validate_connection_arguments(*args: Any | None) -> None:
    if any(all(item is not None for item in combination) for combination in itertools.combinations(args, 2)) or all(
        item is None for item in args
    ):
        raise ValueError(
            "Invalid argument combination. Please provide only 1 of: "
            "connection: redis.asyncio.Redis - direct connection to a Redis instance without pooling; OR"
            "connection_pool: redis.asyncio.ConnectionPool - for pooling connections to a Redis instance; OR"
            "sentinel: redis.asyncio.Sentinel - for managing connections to a set of self-healing Redis nodes."
        )
