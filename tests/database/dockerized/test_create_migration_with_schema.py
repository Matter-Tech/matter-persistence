import sqlalchemy as sa

from matter_persistence.database import DatabaseConfig, get_or_reuse_connection
from matter_persistence.database.migrations.command import create_database_migration
from matter_persistence.database.migrations.utils import async_to_sync


async def test_can_create_version_table_on_the_defined_default_schema(
    start_db_client, temporary_migration_folder, pg_uri
):
    async with get_or_reuse_connection(transactional=True) as saConnection:
        await saConnection.execute(sa.text("CREATE SCHEMA IF NOT EXISTS another_schema;"))

    db_config = DatabaseConfig(
        connection_uri=pg_uri.format(engine="postgresql+asyncpg"),
        migration={
            "path": temporary_migration_folder,
            "file_template": "%%(slug)s",
            "models": [],
            "version_schema": "another_schema",
        },
    )

    await async_to_sync(create_database_migration, db_config, message="Initial migration")

    async with get_or_reuse_connection() as saConnection:
        resp = (
            await saConnection.execute(
                sa.text(
                    """SELECT EXISTS (
    SELECT FROM 
        pg_tables   
    WHERE 
        schemaname = 'another_schema' AND 
        tablename  = 'alembic_version'
    );"""
                )
            )
        ).scalar()

    assert resp is True
