import logging
from collections.abc import Callable
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from matter_persistence.decorators import retry_if_failed
from matter_persistence.sql.base import CustomBase
from matter_persistence.sql.exceptions import DatabaseInvalidSortFieldError, DatabaseNoEngineSetError
from matter_persistence.sql.manager import AsyncSession, DatabaseManager


class SortMethodModel(Enum):
    ASC = "asc"
    DESC = "desc"


async def is_database_alive(database_manager: DatabaseManager):
    """
    Checks if the database is alive or not.
    """
    # many times it is possible to open a connection but the database can't execute a query. Thus,
    # we test also if the query returns the expected result.
    try:
        async with database_manager.session() as session:
            resp = await session.execute(sa.text("SELECT 1"))
            db_result = resp.scalar()
    except DatabaseNoEngineSetError:
        logging.exception("It is not possible to check if the database is alive.")
        return False

    return db_result == 1


async def table_exists(name: str, database_manager: DatabaseManager):
    """
    Checks if a table exists.
    """
    async with database_manager.connect() as conn:
        # Using the inspect() function directly on an AsyncConnection or AsyncEngine object is not currently supported,
        # as there is not yet an awaitable form of the Inspector object available.
        # https://docs.sqlalchemy.org/en/20/errors.html#error-xd3s
        table_names = await conn.run_sync(lambda sync_conn: sa.inspect(sync_conn).get_table_names())

    return name in table_names


@retry_if_failed
async def get(
    session: AsyncSession,
    statement: sa.Select,
    object_class: type[CustomBase] | None = None,
    one_or_none: bool = False,
    with_deleted: bool = False,
):
    result = (
        (await session.execute(statement.where(sa.and_(object_class.deleted.is_(None)))))
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
    db_model: type[CustomBase],
    skip: int = 0,
    limit: int | None = None,
    one_or_none: bool = False,
    with_deleted: bool = False,
    filters: dict | None = None,
    custom_filter: Callable[[sa.Select], sa.Select] | None = None,
    sort_field: str | None = None,
    sort_method: SortMethodModel | None = None,
    joined_field: str | None = None,
):
    q: sa.Select = sa.select(db_model)  # Query is deprecated, hence using Select

    if joined_field:
        q = q.options(joinedload(getattr(db_model, joined_field)))

    if filters is None:
        filters = {}

    for key, value in filters.items():
        if hasattr(db_model, key):
            q = q.filter(getattr(db_model, key) == value)

    if custom_filter:
        q = custom_filter(q)

    if not with_deleted:
        q = q.filter(db_model.deleted.is_(None))

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
        return result.scalar_one_or_none().all()  # type: ignore
    else:
        return result.scalars().all()


@retry_if_failed
async def commit(session: AsyncSession):
    await session.commit()
