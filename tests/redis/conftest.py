from uuid import uuid4

import pytest
from pydantic import BaseModel
from pytest_asyncio import is_async_test
from testcontainers.redis import AsyncRedisContainer

from matter_persistence.redis.manager import CacheManager

ORGANISATION_ID = uuid4()
INTERNAL_ID = uuid4()


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
def cache_manager(async_redis_client):
    return CacheManager(connection=async_redis_client)