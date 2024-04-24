from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError

from matter_persistence.sql.decorators import retry_if_failed
from matter_persistence.sql.exceptions import DatabaseError, DatabaseIntegrityError


@pytest.mark.asyncio
async def test_retry_if_failed_integrity_error():
    mocked_func = MagicMock(side_effect=IntegrityError(None, None, None))
    retry_func = retry_if_failed(mocked_func, (0, 1))
    with pytest.raises(DatabaseIntegrityError):
        await retry_func()


@pytest.mark.asyncio
async def test_retry_if_failed_operational_error():
    mocked_func = MagicMock(side_effect=OperationalError(None, None, None))
    retry_func = retry_if_failed(mocked_func, (0, 1))
    with pytest.raises(DatabaseError):
        await retry_func()


@pytest.mark.asyncio
async def test_retry_if_failed_success():
    async def mocked_func(*args, **kwargs):
        return "Mock Result"

    mocked_func = MagicMock(side_effect=mocked_func)
    retry_func = retry_if_failed(mocked_func)
    res = await retry_func()
    assert res == "Mock Result"
