from sqlalchemy import select

from matter_persistence.sql.utils import get, is_database_alive, table_exists
from tests.sql.conftest import TestBaseDBModel


async def test_is_database_alive(database_session_manager):
    assert await is_database_alive(database_session_manager)


async def test_table_exists_returns_true(insert_test_data, database_session_manager):
    assert await table_exists("test_base_db_model", database_session_manager)


async def test_table_exists_returns_false(database_session_manager):
    assert not await table_exists("table_that_should_not_exist", database_session_manager)


async def test_get_one_or_none(insert_test_data, database_session_manager):
    async with database_session_manager.session() as session:
        res = await get(session, select(TestBaseDBModel.test_field).limit(1), one_or_none=True)
        assert res == 1


async def test_get_without_one_or_none(insert_test_data, database_session_manager):
    async with database_session_manager.session() as session:
        res = await get(session, select(TestBaseDBModel.test_field))
        assert res == 1


async def test_find(insert_test_data, database_session_manager):
    async with database_session_manager.session() as session:
        # TODO fix function, currently it gives "AttributeError: 'datetime.datetime' object has no attribute 'is_'"
        # res = await find(session, TestBaseDBModel)
        # assert res is not None
        pass
