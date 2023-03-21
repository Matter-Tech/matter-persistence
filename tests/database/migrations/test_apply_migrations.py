import os

import pytest

from matter_persistence.database import DatabaseConfig
from matter_persistence.database import get_or_reuse_connection
from matter_persistence.database.migrations.command import (
    apply_database_migration,
    create_database_migration,
    apply,
    create,
)
from matter_persistence.database.migrations.utils import async_to_sync
from .conftest import has_table_been_created


@pytest.mark.asyncio
async def test_can_apply_migration(temporary_migration_folder):
    db_config = DatabaseConfig(
        connection_uri="sqlite+aiosqlite://",
        migration={
            "path": temporary_migration_folder,
            "models": [f"{__package__}.base_model.BaseOrmModel"],
            "file_template": "%%(slug)s",
        },
    )
    await async_to_sync(create_database_migration, db_config, message="Initial migration")

    async with get_or_reuse_connection() as conn:
        await has_table_been_created(conn, "migration_base_orm_model_table", False)

    await async_to_sync(apply_database_migration, db_config)

    # using the same database config to create the objects, because we are using sqlite in memory.
    async with get_or_reuse_connection() as conn:
        await has_table_been_created(conn, "migration_base_orm_model_table", True)


def test_can_apply_migration_from_command(temporary_migration_folder, mocker):
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

    apply("an-ignored-value")
