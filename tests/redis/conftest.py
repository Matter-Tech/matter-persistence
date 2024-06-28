from collections.abc import AsyncGenerator
from unittest.mock import patch
from uuid import uuid4

import pytest
import redis.asyncio
from pydantic import BaseModel
from pytest_asyncio import is_async_test
from testcontainers.compose import DockerCompose
from testcontainers.redis import AsyncRedisContainer

from matter_persistence.redis.manager import CacheManager
from matter_persistence.redis.utils import get_sentinel

ORGANISATION_ID = uuid4()
INTERNAL_ID = uuid4()
TEST_REDIS_PASSWORD = "VerySecretPassword!"


# From stackoverflow:
# By default, pytest-asyncio creates a new event loop per function. If you wish to have asyncio session fixtures,
# your code must run with the same event loop as those fixtures, instead of recreating a new loop each function.
# https://pytest-asyncio.readthedocs.io/en/latest/how-to-guides/run_session_tests_in_same_loop.html
def pytest_collection_modifyitems(items):
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


class TestDTO(BaseModel):
    __test__ = False

    test_field: int


@pytest.fixture
def test_dto():
    return TestDTO(test_field=1)


@pytest.fixture(scope="session")
async def async_redis_client():
    with AsyncRedisContainer() as redis_container:
        async_redis_client = await redis_container.get_async_client()

        yield async_redis_client


@pytest.fixture(scope="session")
async def cache_manager(async_redis_client: redis.asyncio.Redis) -> AsyncGenerator[CacheManager, None]:
    manager = CacheManager(connection=async_redis_client)
    yield manager
    await manager.close_connection_pool()


@pytest.fixture(scope="session")
async def redis_with_sentinels() -> AsyncGenerator[DockerCompose, None]:
    with DockerCompose(
        ".", compose_file_name="docker-compose.yaml", services=["redis-primary", "redis-secondary", "redis-sentinel"]
    ) as compose:
        yield compose


@pytest.fixture(scope="session")
def redis_sentinel_addresses(redis_with_sentinels: DockerCompose) -> list[tuple[str, int]]:
    output = []
    for container in redis_with_sentinels.get_containers():
        if container.Service == "redis-sentinel":
            published_port_spec = container.get_publisher(by_port=26379)
            if published_port_spec.URL and published_port_spec.PublishedPort:
                output.append((published_port_spec.URL, int(published_port_spec.PublishedPort)))
    return output


@pytest.fixture(scope="session")
async def cache_manager_with_sentinel(
    redis_sentinel_addresses: list[tuple[str, int]],
    redis_with_sentinels: DockerCompose,
) -> AsyncGenerator[CacheManager, None]:
    async def _get_master_host(_: str) -> tuple[str, int]:
        return "0.0.0.0", 6379

    sentinel = await get_sentinel(
        sentinel_addresses=redis_sentinel_addresses,
        password=TEST_REDIS_PASSWORD,
    )
    with patch.object(sentinel, sentinel.discover_master.__name__, _get_master_host):
        manager = CacheManager(sentinel=sentinel, sentinel_service_name="mymaster")
        yield manager
        await manager.close_connection_pool()
