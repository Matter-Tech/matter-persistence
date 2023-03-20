from tempfile import TemporaryDirectory

import pytest
import sqlalchemy as sa


@pytest.fixture
def temporary_migration_folder():
    with TemporaryDirectory() as tmpdirname:
        print(f"Created temporary folder for migrations: {tmpdirname}")
        yield tmpdirname


async def has_table_been_created(conn, table_name, expected: bool):
    stmt = sa.text("SELECT EXISTS(SELECT * FROM sqlite_master WHERE type= :table AND name= :table_name)")
    stmt = stmt.bindparams(table="table", table_name=table_name)

    result = await conn.execute(stmt)
    assert bool(result.scalar()) is expected
