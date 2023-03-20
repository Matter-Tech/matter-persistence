import logging
from contextlib import asynccontextmanager
from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncConnection

from .client import DatabaseClient
from .exceptions import DatabaseNoEngineSetException, ConnectionInTransactionException, InvalidPoolStateException

DatabaseAsyncConnection = AsyncConnection
DatabaseAsyncRawConnection = Any


@asynccontextmanager
async def get_or_reuse_connection(
    connection: Optional[DatabaseAsyncConnection] = None, transactional: bool = False
) -> DatabaseAsyncConnection:
    engine = DatabaseClient.get_engine()

    if engine is None:
        raise DatabaseNoEngineSetException

    if connection is None or connection.closed:
        if transactional:
            async with engine.begin() as new_trans_conn:
                yield new_trans_conn
        else:
            async with engine.connect() as new_conn:
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


async def get_raw_driver_connection(sa_connection: DatabaseAsyncConnection) -> DatabaseAsyncRawConnection:
    if sa_connection.in_transaction():
        raise ConnectionInTransactionException(
            "get_raw_driver_connection can't " "be used with a transactional connection"
        )

    for _ in range(DatabaseClient.pool_size):
        raw_connection = await sa_connection.get_raw_connection()
        connection = raw_connection.driver_connection

        logging.debug(f"driver connection id {connection}")
        logging.debug(f"Is sqlAlchemy connection closed? {sa_connection.closed}")

        if sa_connection.engine.name != "sqlite" and connection.is_closed():  # pragma: no cover
            logging.debug("Driver connection is closed. Invalidating it.")
            await sa_connection.invalidate()
        else:
            return connection

    raise InvalidPoolStateException("Not possible to open a valid driver connection. The pool is not in a valid state")
