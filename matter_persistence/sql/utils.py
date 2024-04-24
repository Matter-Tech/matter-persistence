import logging
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import Query, joinedload

from matter_persistence.sql.decorators import retry_if_failed
from matter_persistence.sql.exceptions import DatabaseInvalidSortFieldError, DatabaseNoEngineSetError
from matter_persistence.sql.models import BaseDBModel, SortMethodModel
from matter_persistence.sql.sessions import AsyncSession, DatabaseSessionManager


async def is_database_alive(database_session_manager: DatabaseSessionManager) -> bool:
    """
    Checks if the database is alive or not.
    """
    # many times it is possible to open a connection but the database can't execute a query. Thus,
    # we test also if the query returns the expected result.
    try:
        async with database_session_manager.session() as session:
            resp = await session.execute(sa.text("SELECT 1"))
            db_result = resp.scalar()
    except DatabaseNoEngineSetError:
        logging.exception("It is not possible to check if the database is alive.")
        return False

    return db_result == 1


async def table_exists(name: str, database_session_manager: DatabaseSessionManager):
    """
    Checks if a table exists.
    """
    async with database_session_manager.connect() as conn:
        # Using the inspect() function directly on an AsyncConnection or AsyncEngine object is not currently supported,
        # as there is not yet an awaitable form of the Inspector object available.
        # https://docs.sqlalchemy.org/en/20/errors.html#error-xd3s
        table_names = await conn.run_sync(lambda sync_conn: sa.inspect(sync_conn).get_table_names())

    return name in table_names


def create_table(model_class, database_session_manager: DatabaseSessionManager):
    model_class.__table__.create(database_session_manager._engine)


@retry_if_failed
async def get(
    session: AsyncSession,
    statement: sa.Select[Any],
    object_class: type[BaseDBModel] | None = None,
    one_or_none: bool = False,
    with_deleted: bool = False,
):
    result = (
        (await session.execute(statement.where(sa.and_(object_class.deleted_at.is_(None)))))
        if (object_class and not with_deleted)
        else (await session.execute(statement))
    )

    if one_or_none:
        return result.scalar_one_or_none()
    else:
        return result.scalar()


@retry_if_failed
async def find(
    session: AsyncSession,
    db_model: type[BaseDBModel],
    skip: int = 0,
    limit: int | None = None,
    one_or_none: bool = False,
    with_deleted: bool = False,
    filters: dict | None = None,
    sort_field: str | None = None,
    sort_method: SortMethodModel | None = None,
    joined_field: str | None = None,
):
    q: Query = Query(db_model)

    if joined_field:
        q = q.options(joinedload(getattr(db_model, joined_field)))

    if filters is None:
        filters = {}

    for key, value in filters.items():
        if hasattr(db_model, key):
            q = q.filter(getattr(db_model, key) == value)

    if not with_deleted:
        q = q.filter(db_model.deleted_at.is_(None))

    if sort_field is not None:
        try:
            q = (
                q.order_by(getattr(db_model, sort_field))
                if sort_method == SortMethodModel.ASC
                else q.order_by(getattr(db_model, sort_field).desc())
            )
        except AttributeError as exc:
            raise DatabaseInvalidSortFieldError(
                description=f"The Sort Field '{sort_field}' you selected doesn't exist: {str(exc)}",
                detail={"sort_field": sort_field, "exception": exc},
            )

    if skip:
        q = q.offset(skip)
    if limit:
        q = q.limit(limit)

    result = await session.execute(q)
    if one_or_none:
        items = result.scalar_one_or_none()
    else:
        items = result.all()

    return items


@retry_if_failed
async def commit(session: AsyncSession):
    await session.commit()
