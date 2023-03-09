from matter_persistence.database import DatabaseConfig, DatabaseClient


def test_database_start_should_not_override_engine_if_it_has_been_previously_started():
    config = DatabaseConfig(connection_uri="sqlite+aiosqlite://")

    DatabaseClient.start(config)

    engine_first_id = id(DatabaseClient.get_engine())

    DatabaseClient.start(config)

    engine_second_id = id(DatabaseClient.get_engine())

    assert engine_first_id == engine_second_id
