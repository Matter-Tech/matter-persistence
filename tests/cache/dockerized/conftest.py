import pytest

from matter_persistence.cache import CacheConfig, CacheClient, CacheEngine
from .memcached import MemcachedContainer


@pytest.fixture(scope="session")
def memcached_container():
    memcached = MemcachedContainer()

    memcached.start()

    yield memcached

    # Teardown
    memcached.stop()


@pytest.fixture(scope="session", autouse=True)
def start_cache_client_dockerized(memcached_container):
    host, port = memcached_container.get_host_and_port()
    cache_config = CacheConfig(endpoint=host, port=port, engine=CacheEngine.MEMCACHED)
    CacheClient.start(cache_config)
    yield
