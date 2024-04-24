import asyncio

import pytest
from sqlalchemy import text

from matter_persistence.sql.exceptions import DatabaseNoEngineSetError


async def test_database_session_manager_connection(database_session_manager):
    async with database_session_manager.connect() as conn:
        res = await conn.execute(text("SELECT 1"))
    assert res.scalar() == 1


async def test_database_session_manager_session(database_session_manager):
    async with database_session_manager.session() as session:
        res = await session.execute(text("SELECT 1"))
    assert res.scalar() == 1


async def test_database_session_manager_close_connection(database_session_manager):
    await database_session_manager.close()
    with pytest.raises(DatabaseNoEngineSetError):
        async with database_session_manager.connect() as conn:
            await conn.execute(text("SELECT 1"))


async def test_database_session_manager_close_session(database_session_manager):
    await database_session_manager.close()
    with pytest.raises(DatabaseNoEngineSetError):
        async with database_session_manager.session() as session:
            await session.execute(text("SELECT 1"))
