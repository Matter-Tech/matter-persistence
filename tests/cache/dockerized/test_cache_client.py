from asyncio import sleep

import pytest

from matter_persistence.cache import cache_set, cache_get, cache_delete


@pytest.mark.asyncio
async def test_cache_cycle():
    await cache_set("my-key", 123)
    assert await cache_get("my-key") == 123
    await cache_delete("my-key")
    assert await cache_get("my-key") is None


@pytest.mark.asyncio
async def test_cache_with_timeout():
    await cache_set("my-key", 123, expire_in=1)
    await sleep(1)
    assert await cache_get("my-key") is None
