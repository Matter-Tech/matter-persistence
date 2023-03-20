import inspect
import os

import pytest
from alembic.config import Config

from matter_persistence.database import InvalidDatabaseConfigurationError, DatabaseConfig
from matter_persistence.database.migrations.utils import async_to_sync


@pytest.mark.asyncio
async def test_async_to_sync_throws_exception_when_migration_path_is_not_set():
    """Test The package does not contain a DatabaseConfig instance."""
    with pytest.raises(InvalidDatabaseConfigurationError):
        await async_to_sync(lambda x: x, db_config=DatabaseConfig(connection_uri="sqlite+aiosqlite://"))


@pytest.mark.asyncio
async def test_async_to_sync_throws_exception_when_migration_path_does_not_exist():
    """Test The package does not contain a DatabaseConfig instance."""
    with pytest.raises(InvalidDatabaseConfigurationError):
        await async_to_sync(
            lambda x: x,
            db_config=DatabaseConfig(
                connection_uri="sqlite+aiosqlite://", migration={"path": "non-existing-path", "models": []}
            ),
        )


@pytest.mark.asyncio
async def test_async_to_sync_calls_target_function_with_a_sync_connection(temporary_migration_folder):
    db_config = DatabaseConfig(
        connection_uri="sqlite+aiosqlite://", migration={"path": temporary_migration_folder, "models": []}
    )

    def target_function(connection, passed_config):
        base_dir = os.path.abspath(os.path.dirname(inspect.getfile(async_to_sync)))
        expected_script_location = os.path.join(base_dir, "resources")
        expected_version_location = os.path.join(temporary_migration_folder)

        # validating the sqlalchemy synchronous configuration set
        assert connection is not None
        assert connection.closed is False
        assert str(connection.engine.url) == db_config.connection_uri

        # validating the alembic configuration set
        assert type(passed_config) is Config
        assert passed_config.attributes["db_config"] == db_config

        assert (
            passed_config.get_main_option("file_template")
            == "%(year)d%(month).2d%(day).2d-%(hour).2d%(minute).2d%(second).2d-%(slug)s"
        )

        assert passed_config.get_main_option("script_location") == expected_script_location
        assert passed_config.get_main_option("version_locations") == expected_version_location

    await async_to_sync(target_function, db_config)
