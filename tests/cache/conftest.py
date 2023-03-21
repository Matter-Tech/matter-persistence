import pytest

from matter_persistence.cache import CacheConfig, CacheClient


@pytest.fixture
async def start_cache_client():
    config = CacheConfig()

    CacheClient.start(config)
    yield config
    await CacheClient.clear()
