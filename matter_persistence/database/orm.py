from typing import Union
from uuid import UUID

from sqlalchemy.orm import DeclarativeBase

from .exceptions import InstanceNotFoundError
from .session import get_or_reuse_session


class DatabaseBaseModel(DeclarativeBase):
    deleted: bool

    async def save(self):
        async with get_or_reuse_session(transactional=True) as session:
            session.add(self)

    @classmethod
    async def get(cls, pk: Union[str, int, UUID]):
        async with get_or_reuse_session() as session:
            obj = await session.get(cls, ident=pk)

        if obj is None:
            raise InstanceNotFoundError(message=f"Object of type {cls}:{pk} not found.")

        return obj

    async def delete(self):
        async with get_or_reuse_session(transactional=True) as session:
            await session.delete(self)
            self.deleted = True
