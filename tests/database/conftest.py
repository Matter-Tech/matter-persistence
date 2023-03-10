import pytest

from matter_persistence.database import DatabaseConfig, DatabaseClient


@pytest.fixture
async def start_database_client():
    config = DatabaseConfig(connection_uri="sqlite+aiosqlite://")

    DatabaseClient.start(config)
    yield
    await DatabaseClient.stop()
    DatabaseClient.destroy()


@pytest.fixture(autouse=True)
async def stopping_database_client():
    yield
