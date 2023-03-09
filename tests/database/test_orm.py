import pytest
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from matter_persistence.database import DatabaseBaseModel
from matter_persistence.database import get_or_reuse_connection


class BaseOrmModel(DatabaseBaseModel):
    __tablename__ = "base_table"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))


@pytest.fixture
async def configure_base_class(start_database_client):
    async with get_or_reuse_connection(transactional=True) as conn:
        await conn.run_sync(DatabaseBaseModel.metadata.create_all)


@pytest.mark.asyncio
async def test_base_save_and_retrieve(configure_base_class):
    b = BaseOrmModel(id=1, name="a name")
    await b.save()

    b1 = await BaseOrmModel.get(pk=1)

    assert b1.name == b.name
