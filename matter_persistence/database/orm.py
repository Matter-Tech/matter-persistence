from typing import Union, List
from uuid import UUID

import sqlalchemy
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import DeclarativeBase

from .exceptions import InstanceNotFoundError, InvalidActionError
from .session import get_or_reuse_session


class DatabaseBaseModel(DeclarativeBase):
    async def save(self):
        async with get_or_reuse_session(transactional=True) as session:
            session.add(self)
        self._deleted = False

    async def delete(self):
        if self.deleted:
            raise InvalidActionError("Can't delete a deleted object.")

        try:
            async with get_or_reuse_session(transactional=True) as session:
                await session.delete(self)
            self._deleted = True

        except InvalidRequestError:
            raise InvalidActionError("Can't delete a not persisted object.")

    @property
    def deleted(self) -> bool:
        return bool(getattr(self, "_deleted", False)) is True

    @classmethod
    async def get(cls, ident: Union[str, int, UUID]):
        async with get_or_reuse_session() as session:
            obj = await session.get(cls, ident=ident)

        if obj is None:
            raise InstanceNotFoundError(message=f"Object of type {cls}:{ident} not found.")

        return obj

    @classmethod
    async def list(
        cls,
        *where_clause,
        limit=100,
        offset=0,
        ordered_by: List[Union[sqlalchemy.Column | sqlalchemy.ColumnClause]] | None = None,
    ):
        stmt = sqlalchemy.select(cls)

        if len(where_clause) > 0:
            stmt = stmt.where(*where_clause)

        if not bool(ordered_by):
            ordered_by = getattr(cls, "default_order", [])

        if bool(ordered_by):
            stmt = stmt.order_by(*ordered_by)

        if offset:
            stmt = stmt.offset(offset)

        stmt = stmt.limit(limit=limit)

        async with get_or_reuse_session() as session:
            result = await session.execute(stmt)
            objects = result.scalars().all()

        return objects
