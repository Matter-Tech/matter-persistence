import pytest

from matter_persistence.database.connection import (
    get_or_reuse_connection,
    get_raw_driver_connection,
)


@pytest.mark.asyncio
async def test_get_raw_driver_connect_cant_be_used_with_transactional_sa_connection(start_database_client):
    async with get_or_reuse_connection() as saConnection:
        async with saConnection.begin():
            with pytest.raises(Exception):
                await get_raw_driver_connection(saConnection)
