from sqlalchemy import select

from matter_persistence.sql.utils import commit, find, get, is_database_alive, table_exists
from tests.sql.conftest import NUM_ROWS_IN_TABLE, NumberORM, test_data


async def test_is_database_alive_success(database_manager):
    assert await is_database_alive(database_manager)


async def test_is_database_alive_unsuccess(database_manager):
    await database_manager.close()
    assert not await is_database_alive(database_manager)


async def test_table_exists_returns_true(postgres_db, database_manager):
    assert await table_exists("numbers", database_manager)


async def test_table_exists_returns_false(database_manager):
    assert not await table_exists("table_that_should_not_exist", database_manager)


async def test_get_with_one_or_none(postgres_db, database_manager):
    async with database_manager.session() as session:
        res = await get(session, select(NumberORM.number).limit(1), one_or_none=True)
        assert res == test_data[0]["number"]


async def test_get_without_one_or_none(postgres_db, database_manager):
    async with database_manager.session() as session:
        res = await get(session, select(NumberORM.number))
        assert res == test_data[0]["number"]


async def test_find(postgres_db, database_manager):
    async with database_manager.session() as session:
        res = await find(session, NumberORM)
        assert len(res) == NUM_ROWS_IN_TABLE


async def test_find_with_filter(postgres_db, database_manager):
    async with database_manager.session() as session:
        res = await find(session, NumberORM, filters={"number": test_data[0]["number"]})
        assert len(res) == 1  # only one row is expected
        # test CustomBase
        assert res[0].created
        assert res[0].updated
        assert res[0].deleted is None


async def test_find_with_limit(postgres_db, database_manager):
    async with database_manager.session() as session:
        res = await find(session, NumberORM, limit=1)
        assert len(res) == 1  # only one row is expected


async def test_commit(postgres_db, database_manager):
    async with database_manager.session() as session:
        session.add(NumberORM(number=len(test_data) + 1))
        await commit(session)
        res = await find(session, NumberORM)
        assert len(res) == len(test_data) + 1
