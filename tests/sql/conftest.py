import pytest
from sqlalchemy import insert
from sqlalchemy.orm import Mapped

from matter_persistence.sql.base import Base, CustomBase
from matter_persistence.sql.manager import DatabaseManager

# test database settings
POSTGRES_PORT = 5432
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_DB = "postgres"

CONNECTION_URI = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}"

NUM_ROWS_IN_TABLE = 2

# this is used to compare the fields that have been set by using datetime.now()
# only a few seconds of difference can be expected between the set field and the compared datetime,
# so 1 min should be super safe
one_min_difference_in_secs = 60


class TestBaseDBModel(CustomBase):
    __tablename__ = "test_base_db_model"
    __test__ = False

    test_field: Mapped[int]


test_data = [{"test_field": x} for x in range(NUM_ROWS_IN_TABLE)]


@pytest.fixture
def database_manager():
    return DatabaseManager(CONNECTION_URI)


@pytest.fixture(scope="session", autouse=True)
async def insert_test_data():
    database_manager = DatabaseManager(CONNECTION_URI)

    async with database_manager.connect() as conn:
        print("creating test table")
        await conn.run_sync(Base.metadata.create_all)
        print("inserting test data")
        for data in test_data:
            await conn.execute(insert(TestBaseDBModel), data)
        await conn.commit()

    yield

    async with database_manager.connect() as conn:
        print("dropping test table")
        await conn.run_sync(Base.metadata.drop_all)

    await database_manager.close()
