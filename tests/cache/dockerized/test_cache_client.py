from asyncio import sleep


from matter_persistence.cache import cache_set, cache_get, cache_delete


async def test_cache_cycle(start_cache_client_dockerized):
    await cache_set("my-key", 123)
    assert await cache_get("my-key") == 123
    await cache_delete("my-key")
    assert await cache_get("my-key") is None


async def test_cache_with_timeout(start_cache_client_dockerized):
    await cache_set("my-key", 123, expire_in=1)
    await sleep(1)
    assert await cache_get("my-key") is None
