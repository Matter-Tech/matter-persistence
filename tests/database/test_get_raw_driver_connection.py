import pytest

from matter_persistence.database.exceptions import ConnectionInTransactionException
from matter_persistence.database.connection import (
    get_or_reuse_connection,
    get_raw_driver_connection,
)


@pytest.mark.asyncio
async def test_get_raw_driver_connect_cant_be_used_with_transactional_sa_connection(start_database_client):
    async with get_or_reuse_connection(transactional=True) as saConnection:
        with pytest.raises(ConnectionInTransactionException):
            await get_raw_driver_connection(saConnection)


@pytest.mark.asyncio
async def test_get_raw_driver_connect_happy_path(start_database_client):
    async with get_or_reuse_connection() as saConnection:
        raw_connection = await get_raw_driver_connection(saConnection)

    assert raw_connection is not None
    resp = await raw_connection.execute("select 1")
    value = await resp.fetchone()
    assert value[0] == 1
