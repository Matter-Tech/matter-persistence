from typing import Union
from uuid import UUID

from sqlalchemy.orm import DeclarativeBase

from .session import get_or_reuse_session


class DatabaseBaseModel(DeclarativeBase):
    async def save(self):
        async with get_or_reuse_session(transactional=True) as session:
            session.add(self)

    @classmethod
    async def get(cls, pk: Union[str, int, UUID]):
        async with get_or_reuse_session(transactional=True) as session:
            obj = await session.get(cls, ident=pk)
        return obj
