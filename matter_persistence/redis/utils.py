import gzip
import pickle
from functools import lru_cache
from typing import Any

from redis import asyncio as aioredis


@lru_cache(maxsize=1)
def get_connection_pool(host: str, port: int, db: int = 0) -> aioredis.ConnectionPool:
    """
    Gets a connection pool to Redis. Note that it's a singleton - an application process should always only
    create 1 connection pool & reuse it for all internal connections.

    Args:
        host (str): Redis host
        port (int): Redis port
        db (int): Redis logical database, normally only 0 is used

    Returns:
        connection_pool (aioredis.ConnectionPool): a connection pool to be reused by connections
            established in the application
    """
    return aioredis.ConnectionPool.from_url(f"redis://{host}:{port}/{db}")


def compress_pickle_data(data: Any) -> bytes:
    pickled_data = pickle.dumps(data)  # Serialize the data into bytes using pickle
    compressed_data = gzip.compress(pickled_data)  # Compress the pickled data using gzip
    return compressed_data


def decompress_pickle_data(compressed_data: bytes) -> Any:
    decompressed_data = gzip.decompress(compressed_data)  # Decompress the compressed data using gzip
    data = pickle.loads(decompressed_data)  # Deserialize the data back into Python objects using pickle
    return data
