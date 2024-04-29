from unittest.mock import MagicMock

import pytest
from redis.exceptions import ConnectionError, TimeoutError
from sqlalchemy.exc import IntegrityError, OperationalError

from matter_persistence.decorators import retry_if_failed
from matter_persistence.redis.exceptions import CacheServerError
from matter_persistence.sql.exceptions import DatabaseError, DatabaseIntegrityError


async def test_retry_if_failed_connection_error():
    mocked_func = MagicMock(side_effect=ConnectionError)
    retry_func = retry_if_failed(mocked_func, (0, 1))
    with pytest.raises(CacheServerError):
        await retry_func()


async def test_retry_if_failed_timeout_error():
    mocked_func = MagicMock(side_effect=TimeoutError)
    retry_func = retry_if_failed(mocked_func, (0, 1))
    with pytest.raises(CacheServerError):
        await retry_func()


async def test_retry_if_failed_success():
    async def mocked_func(*args, **kwargs):
        return "Mock Result"

    mocked_func = MagicMock(side_effect=mocked_func)
    retry_func = retry_if_failed(mocked_func)
    _ = await retry_func()


async def test_retry_if_failed_integrity_error():
    mocked_func = MagicMock(side_effect=IntegrityError(None, None, None))
    retry_func = retry_if_failed(mocked_func, (0, 1))
    with pytest.raises(DatabaseIntegrityError):
        await retry_func()


async def test_retry_if_failed_operational_error():
    mocked_func = MagicMock(side_effect=OperationalError(None, None, None))
    retry_func = retry_if_failed(mocked_func, (0, 1))
    with pytest.raises(DatabaseError):
        await retry_func()
