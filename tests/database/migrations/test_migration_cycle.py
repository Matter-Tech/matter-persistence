import os.path

import pytest

from matter_persistence.database import DatabaseConfig
from matter_persistence.database import get_or_reuse_connection
from matter_persistence.database.migrations.command import apply_database_migration, create_database_migration
from matter_persistence.database.migrations.utils import async_to_sync
from .conftest import has_table_been_created


@pytest.mark.asyncio
async def test_create_and_apply_migrations(temporary_migration_folder):
    db_config = DatabaseConfig(
        connection_uri="sqlite+aiosqlite://",
        migration={
            "path": temporary_migration_folder,
            "models": [f"{__package__}.base_model.BaseOrmModel"],
            "file_template": "%%(slug)s",
        },
    )

    # Fist migration created
    await async_to_sync(create_database_migration, db_config, message="Initial migration")

    async with get_or_reuse_connection() as conn:
        await has_table_been_created(conn, "migration_base_orm_model_table", False)
        await has_table_been_created(conn, "another_class_to_be_migrated_later", False)

    # Fist migration applied
    await async_to_sync(apply_database_migration, db_config)

    # using the same database config to create the objects, because we are using sqlite in memory.
    async with get_or_reuse_connection() as conn:
        await has_table_been_created(conn, "migration_base_orm_model_table", True)
        await has_table_been_created(conn, "another_class_to_be_migrated_later", False)

    db_config = DatabaseConfig(
        connection_uri="sqlite+aiosqlite://",
        migration={
            "path": temporary_migration_folder,
            "models": [
                f"{__package__}.base_model.BaseOrmModel",
                f"{__package__}.another_model.AnotherClassToBeMigratedLater",
            ],
            "file_template": "%%(slug)s",
        },
    )

    await async_to_sync(create_database_migration, db_config, message="introducing another migration")

    assert os.path.exists(os.path.join(temporary_migration_folder, "introducing_another_migration.py"))

    # Second migration applied
    await async_to_sync(apply_database_migration, db_config)

    async with get_or_reuse_connection() as conn:
        await has_table_been_created(conn, "migration_base_orm_model_table", True)
        await has_table_been_created(conn, "another_class_to_be_migrated_later", True)
