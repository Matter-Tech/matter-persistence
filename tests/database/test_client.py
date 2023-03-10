import pytest

from matter_persistence.database import DatabaseConfig, DatabaseClient


def test_database_start_should_not_override_engine_if_it_has_been_previously_started():
    config = DatabaseConfig(connection_uri="sqlite+aiosqlite://")

    DatabaseClient.start(config)

    engine_first_id = id(DatabaseClient.get_engine())

    DatabaseClient.start(config)

    engine_second_id = id(DatabaseClient.get_engine())

    assert engine_first_id == engine_second_id


def test_database_destroy():
    config = DatabaseConfig(connection_uri="sqlite+aiosqlite://")

    DatabaseClient.start(config)

    DatabaseClient.destroy()

    assert DatabaseClient.get_engine() is None


def test_database_destroy_not_started_client():
    assert DatabaseClient.get_engine() is None

    DatabaseClient.destroy()

    assert DatabaseClient.get_engine() is None


@pytest.mark.asyncio
async def test_database_stop_not_started_client():
    assert DatabaseClient.get_engine() is None

    await DatabaseClient.stop()

    assert DatabaseClient.get_engine() is None
