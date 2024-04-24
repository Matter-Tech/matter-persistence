import time
from datetime import UTC, datetime

import pytest
from sqlalchemy import insert
from sqlalchemy.orm import Mapped

from matter_persistence.sql.base import Base, IntID
from matter_persistence.sql.models import BaseDBModel
from matter_persistence.sql.sessions import DatabaseSessionManager

# test database settings
POSTGRES_PORT = 5432
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_DB = "postgres"

CONNECTION_URI = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}"


# this is used to compare the fields that have been set by using datetime.now()
# only a few seconds of difference can be expected between the set field and the compared datetime,
# so 1 min should be super safe
one_min_difference_in_secs = 60


class TestBaseDBModel(Base, BaseDBModel, IntID):
    __tablename__ = "test_base_db_model"
    __test__ = False

    test_field: Mapped[int]


# make test rows that are inserted during test setup
test_data_1 = TestBaseDBModel(
    test_field=1,
    created_at=datetime.now(tz=UTC),  # noqa
    created_at_timestamp=time.time(),  # noqa
    updated_at=datetime.now(tz=UTC),  # noqa
    deleted_at=datetime.now(tz=UTC),  # noqa
)

test_data_2 = TestBaseDBModel(
    test_field=2,
    created_at=datetime.now(tz=UTC),  # noqa
    created_at_timestamp=time.time(),  # noqa
    updated_at=datetime.now(tz=UTC),  # noqa
    deleted_at=datetime.now(tz=UTC),  # noqa
)


@pytest.fixture
def test_base_db_model():
    return TestBaseDBModel(test_field=1)


@pytest.fixture
def database_session_manager():
    return DatabaseSessionManager(CONNECTION_URI)


@pytest.fixture(scope="session", autouse=True)
async def insert_test_data():
    database_session_manager = DatabaseSessionManager(CONNECTION_URI)

    async with database_session_manager.connect() as conn:
        print("creating test table")
        await conn.run_sync(Base.metadata.create_all)
        print("inserting test data")
        await conn.execute(insert(TestBaseDBModel), test_data_1.as_dict())
        await conn.execute(insert(TestBaseDBModel), test_data_2.as_dict())
        await conn.commit()

    yield

    async with database_session_manager.connect() as conn:
        print("dropping test table")
        await conn.run_sync(Base.metadata.drop_all)

    await database_session_manager.close()
