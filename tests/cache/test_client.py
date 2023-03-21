from asyncio import sleep

import pytest

from matter_persistence.cache import cache_get, cache_set, cache_delete


class AClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b


@pytest.mark.asyncio
async def test_cache_get_base_case(start_cache_client):
    assert await cache_get("non_existent_key") is None


@pytest.mark.asyncio
async def test_cache_get_n_set(start_cache_client):
    instance = AClass(1, 2)

    await cache_set("my-key", instance)

    returned_instance = await cache_get("my-key")

    assert returned_instance.a == 1
    assert returned_instance.b == 2


@pytest.mark.asyncio
async def test_cache_get_n_set_with_expire(start_cache_client):
    instance = AClass(1, 2)

    await cache_set("my-key", instance, expire_in=1)
    await sleep(1)
    assert await cache_get("my-key") is None


@pytest.mark.asyncio
async def test_cache_set_n_delete(start_cache_client):
    await cache_set("my-key", 123)
    await cache_delete("my-key")
    assert await cache_get("my-key") is None
