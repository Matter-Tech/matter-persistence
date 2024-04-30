import pytest

from matter_persistence.redis.async_redis_client import AsyncRedisClient


def test_async_redis_client_incorrect_argument_combination():
    with pytest.raises(ValueError):
        _ = AsyncRedisClient(connection=None, connection_pool=None)


async def test_async_redis_client_set_hash_field(async_redis_client):
    redis_client = AsyncRedisClient(connection=async_redis_client)
    res = await redis_client.set_hash_field(hash_key="foo", field="some", value="bar")
    assert res
