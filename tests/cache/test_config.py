import pytest

from matter_persistence.cache import CacheEngine, CacheConfig
from matter_persistence.cache import InvalidCacheConfigurationError


def test_config_throws_exception_when_engine_is_not_memory_and_no_endpoint_is_set():
    with pytest.raises(InvalidCacheConfigurationError):
        CacheConfig(engine=CacheEngine.MEMCACHED)
