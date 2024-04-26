from sqlalchemy import select

from matter_persistence.sql.utils import find, get, is_database_alive, table_exists, commit
from tests.sql.conftest import TestBaseDBModel, NUM_ROWS_IN_TABLE, test_data


async def test_is_database_alive_success(database_manager):
    assert await is_database_alive(database_manager)


async def test_is_database_alive_unsuccess(database_manager):
    await database_manager.close()
    assert not await is_database_alive(database_manager)


async def test_table_exists_returns_true(insert_test_data, database_manager):
    assert await table_exists("test_base_db_model", database_manager)


async def test_table_exists_returns_false(database_manager):
    assert not await table_exists("table_that_should_not_exist", database_manager)


async def test_get_with_one_or_none(insert_test_data, database_manager):
    async with database_manager.session() as session:
        res = await get(session, select(TestBaseDBModel.test_field).limit(1), one_or_none=True)
        assert res == test_data[0]["test_field"]


async def test_get_without_one_or_none(insert_test_data, database_manager):
    async with database_manager.session() as session:
        res = await get(session, select(TestBaseDBModel.test_field))
        assert res == test_data[0]["test_field"]


async def test_find(insert_test_data, database_manager):
    async with database_manager.session() as session:
        res = await find(session, TestBaseDBModel)
        assert len(res) == NUM_ROWS_IN_TABLE


async def test_find_with_filter(insert_test_data, database_manager):
    async with database_manager.session() as session:
        res = await find(session, TestBaseDBModel, filters={"test_field": test_data[0]["test_field"]})
        assert len(res) == 1  # only one row is expected


async def test_find_with_limit(insert_test_data, database_manager):
    async with database_manager.session() as session:
        res = await find(session, TestBaseDBModel, limit=1)
        assert len(res) == 1  # only one row is expected


async def test_commit(insert_test_data, database_manager):
    async with database_manager.session() as session:
        session.add(TestBaseDBModel(test_field=len(test_data) + 1))
        await commit(session)
        res = await find(session, TestBaseDBModel)
        assert len(res) == len(test_data) + 1
