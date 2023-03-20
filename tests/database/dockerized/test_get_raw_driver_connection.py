from asyncio import sleep

import pytest
import sqlalchemy as sa

from matter_persistence.database import get_or_reuse_connection, get_raw_driver_connection


@pytest.mark.asyncio
async def test_get_raw_connection_returns_a_valid_asyncpg_object(external_connection):
    pid1 = None
    is_closed_1 = None

    try:
        async with get_or_reuse_connection() as saConnection:
            pid1 = (await saConnection.execute(sa.text("SELECT pg_backend_pid();"))).scalar()

            # putting the pool in a wrong state
            # Terminates the connection from the db's side
            assert (await external_connection.fetchval(f"SELECT pg_terminate_backend({pid1})")) is True
            # give it some time for the events being processed
            await sleep(1)

            raw_connection = await saConnection.get_raw_connection()
            asyncpg_connection = raw_connection.driver_connection
            is_closed_1 = asyncpg_connection.is_closed()
    except Exception:
        # We wrap the call logic in a try/except construct to not raise error in the test because SQLAlchemy tries to
        # rollback a dead connection
        pass

    async with get_or_reuse_connection() as saConnection:
        asyncpg_connection = await get_raw_driver_connection(saConnection)
        is_closed_2 = asyncpg_connection.is_closed()
        pid2 = await asyncpg_connection.fetchval("SELECT pg_backend_pid();")

        assert pid1 is not None
        assert pid2 is not None
        assert pid2 != pid1
        assert is_closed_1 is True
        assert is_closed_2 is False


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_derived_raw_driver_connection_directly_from_sqAlc_connection_can_lead_to_use_a_closed_asyncpg_object(
    external_connection,
):
    try:
        is_closed = False
        async with get_or_reuse_connection() as saConnection:
            pid = (await saConnection.execute(sa.text("SELECT pg_backend_pid();"))).scalar()
            # Terminates the connection from the db's side
            assert (await external_connection.fetchval(f"SELECT pg_terminate_backend({pid})")) is True
            # give it some time for the events being processed
            await sleep(1)

            raw_connection = await saConnection.get_raw_connection()
            raw_driver_connection = raw_connection.driver_connection
            is_closed = raw_driver_connection.is_closed()
    except Exception:
        # We wrap the call logic in a try/except construct to not raise error in the test because SQLAlchemy tries to
        # rollback a dead connection
        pass
    finally:
        assert is_closed is True
