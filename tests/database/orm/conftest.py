from typing import List

import pytest
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from matter_persistence.database import DatabaseBaseModel
from matter_persistence.database import get_or_reuse_connection


class BaseOrmModel(DatabaseBaseModel):
    __tablename__ = "base_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))

    anothers_orm: Mapped[List["AnotherOrmModel"]] = relationship(back_populates="base")


class AnotherOrmModel(DatabaseBaseModel):
    __tablename__ = "another_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))

    base_id: Mapped[int] = mapped_column(ForeignKey("base_table.id"), nullable=False)

    base: Mapped[BaseOrmModel] = relationship(back_populates="anothers_orm")


@pytest.fixture
async def configure_base_class(start_database_client):
    # Ensuring the class exists and the database is empty
    async with get_or_reuse_connection(transactional=True) as conn:
        await conn.run_sync(DatabaseBaseModel.metadata.create_all)
