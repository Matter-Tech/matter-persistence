from contextlib import asynccontextmanager
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .client import DatabaseClient

DatabaseOrmAsyncSession = AsyncSession


@asynccontextmanager
async def get_or_reuse_session(
    session: Optional[DatabaseOrmAsyncSession] = None, transactional: bool = False
) -> DatabaseOrmAsyncSession:
    if session is None:
        _session = async_sessionmaker(DatabaseClient.get_engine(), expire_on_commit=False)
        if transactional:
            async with _session.begin() as _session_conn:
                yield _session_conn
        else:
            async with _session() as _session_new:
                yield _session_new
    else:
        if transactional:
            if session.in_transaction():
                async with session.begin_nested():
                    # This starts us another, nested transaction.
                    # Note that we still return the same connection, but this nested transaction context manager
                    # still manages rollback
                    yield session
            else:
                async with session.begin():
                    yield session
        else:
            yield session
