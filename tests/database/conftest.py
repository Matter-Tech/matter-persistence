from tempfile import TemporaryDirectory

import pytest

from matter_persistence.database import DatabaseConfig, DatabaseClient


@pytest.fixture
async def start_database_client():
    config = DatabaseConfig(connection_uri="sqlite+aiosqlite://")

    DatabaseClient.start(config)
    yield config


@pytest.fixture(autouse=True)
async def stopping_database_client():
    yield
    await DatabaseClient.stop()
    DatabaseClient.destroy()


@pytest.fixture
def temporary_migration_folder():
    with TemporaryDirectory() as tmpdirname:
        print(f"Created temporary folder for migrations: {tmpdirname}")
        yield tmpdirname
