import os.path

import pytest as pytest

from matter_persistence.database import DatabaseConfig
from matter_persistence.database.migrations.command import create_database_migration, create
from matter_persistence.database.migrations.utils import async_to_sync


@pytest.mark.asyncio
async def test_can_create_migration(temporary_migration_folder):
    db_config = DatabaseConfig(
        connection_uri="sqlite+aiosqlite://",
        migration={
            "path": temporary_migration_folder,
            "models": [f"{__package__}.base_model.BaseOrmModel"],
            "file_template": "%%(slug)s",
        },
    )

    await async_to_sync(create_database_migration, db_config, message="Initial migration")

    assert os.path.exists(os.path.join(temporary_migration_folder, "initial_migration.py"))


@pytest.mark.asyncio
async def test_can_create_migration_without_models(temporary_migration_folder):
    """It will create an empty migration"""
    db_config = DatabaseConfig(
        connection_uri="sqlite+aiosqlite://",
        migration={"path": temporary_migration_folder, "file_template": "%%(slug)s", "models": []},
    )

    await async_to_sync(create_database_migration, db_config, message="empty migration")

    assert os.path.exists(os.path.join(temporary_migration_folder, "empty_migration.py"))


def test_can_create_migration_from_command(temporary_migration_folder, mocker):
    db_config = DatabaseConfig(
        connection_uri="sqlite+aiosqlite://",
        migration={
            "path": temporary_migration_folder,
            "models": [f"{__package__}.base_model.BaseOrmModel"],
            "file_template": "%%(slug)s",
        },
    )

    mocker.patch("matter_persistence.database.migrations.command.load_db_config", return_value=db_config)

    create("an-ignored-value", message="Another migration")

    assert os.path.exists(os.path.join(temporary_migration_folder, "another_migration.py"))


@pytest.mark.asyncio
async def test_can_create_migration_with_another_schema(temporary_migration_folder):
    db_config = DatabaseConfig(
        connection_uri="sqlite+aiosqlite://",
        migration={
            "path": temporary_migration_folder,
            "models": [f"{__package__}.base_model.BaseOrmModel"],
            "file_template": "%%(slug)s",
            "default_schema": "another_schema",
        },
    )

    await async_to_sync(create_database_migration, db_config, message="Initial migration")

    assert os.path.exists(os.path.join(temporary_migration_folder, "initial_migration.py"))
