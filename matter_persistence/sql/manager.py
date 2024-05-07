import contextlib
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from matter_persistence.sql.exceptions import DatabaseNoEngineSetError


class DatabaseManager:
    """
    Class: DatabaseManager

    A class for managing database connections in an asynchronous manner.

    Methods:
    - __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        Initializes the DatabaseManager object with the given host and optional engine arguments.
        Args:
            - host (str): The host name or connection URI of the database.
            - engine_kwargs (dict[str, Any]): Optional keyword arguments to be passed to the create_async_engine function.

    - __aenter__(self) -> DatabaseManager:
        Async context manager method for entering a context.
        Returns:
            - DatabaseManager: The current DatabaseManager object.

    - __aexit__(self, exc_type, exc_value, traceback):
        Async context manager method for exiting a context.
        Args:
            - exc_type: The type of the exception, if one occurred.
            - exc_value: The value of the exception.
            - traceback: The traceback of the exception.

    - close(self):
        Closes the database session manager.
        Raises:
            - Exception: If the DatabaseManager is not initialized.

    - connect(self) -> AsyncIterator[AsyncConnection]:
        Async context manager for creating and managing a database connection.
        Yields:
            - AsyncConnection: The database connection object.
        Raises:
            - DatabaseNoEngineSetError: If the DatabaseManager is not initialized.

    - session(self) -> AsyncIterator[AsyncSession]:
        Async context manager for creating and managing a database session.
        Yields:
            - AsyncSession: The database session object.
        Raises:
            - DatabaseNoEngineSetError: If the DatabaseManager is not initialized.

    """

    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine, expire_on_commit=False)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise DatabaseNoEngineSetError(
                description="DatabaseManager is not initialized",
            )

        async with self._engine.begin() as connection:
            try:
                yield connection
            except:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise DatabaseNoEngineSetError(
                description="DatabaseManager is not initialized",
            )

        session = self._sessionmaker()
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()
