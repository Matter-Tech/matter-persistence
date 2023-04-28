import sqlalchemy as sa


async def has_table_been_created(conn, table_name, expected: bool):
    stmt = sa.text("SELECT EXISTS(SELECT * FROM sqlite_master WHERE type= :table AND name= :table_name)")
    stmt = stmt.bindparams(table="table", table_name=table_name)

    result = await conn.execute(stmt)
    assert bool(result.scalar()) is expected
