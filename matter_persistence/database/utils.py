import logging

import sqlalchemy as sa

from .connection import get_or_reuse_connection
from .exceptions import DatabaseNoEngineSetException


async def is_database_alive() -> bool:
    # many times it is possible to open a connection but the database can't execute a query. Thus,
    # we test also if the query returns the expected result.
    try:
        async with get_or_reuse_connection() as conn:
            resp = await conn.execute(sa.text("SELECT 1"))
            db_result = resp.scalar()
    except DatabaseNoEngineSetException:
        logging.exception("Not possible to check if the database is alive")
        return False

    return db_result == 1
