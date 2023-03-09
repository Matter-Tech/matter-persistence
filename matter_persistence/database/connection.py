import logging
from contextlib import asynccontextmanager
from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncConnection

from .client import DatabaseClient


@asynccontextmanager
async def get_or_reuse_connection(
    connection: Optional[AsyncConnection] = None, transactional: bool = False
) -> AsyncConnection:
    if connection is None or connection.closed:
        if transactional:
            async with DatabaseClient.get_engine().begin() as new_trans_conn:
                yield new_trans_conn
        else:
            async with DatabaseClient.get_engine().connect() as new_conn:
                yield new_conn
    else:
        if transactional:
            if connection.in_transaction():
                async with connection.begin_nested():
                    # This starts us another, nested transaction.
                    # Note that we still return the same connection, but this nested transaction context manager
                    # still manages rollback
                    yield connection
            else:
                async with connection.begin():
                    yield connection
        else:
            yield connection


async def get_raw_driver_connection(sa_connection: AsyncConnection) -> Any:
    if sa_connection.in_transaction():
        raise Exception("get_raw__driver_connection can't be used with a transactional sqlAlchemy connections")

    for _ in range(DatabaseClient.pool_size):
        raw_connection = await sa_connection.get_raw_connection()
        connection = raw_connection.driver_connection

        logging.debug(f"asyncPG connection id {connection}")
        logging.debug(f"Is asyncPG connection closed? {connection.is_closed()}")
        logging.debug(f"Is sqlAlchemy connection closed? {sa_connection.closed}")

        if connection.is_closed():
            await sa_connection.invalidate()
        else:
            return connection

    raise Exception("Not possible to open a valid driver connection")
