import pytest
from testcontainers.postgres import PostgresContainer
from asyncpg import create_pool

from matter_persistence.database import DatabaseClient, DatabaseConfig

TEST_DB_USER = "testdb"
TEST_DB_PASSWORD = "pass"
TEST_DB_NAME = "testdb"
TEST_DB_PORT = "5432"


@pytest.fixture(scope="session")
def postgres_container():
    """
    PostgreSQL client scoped for module.

    Connects to a containerized database, with migrations.
    """
    postgres = PostgresContainer(
        "postgres:latest",
        port=TEST_DB_PORT,
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD,
        dbname=TEST_DB_NAME,
    )

    postgres.start()

    yield postgres

    # Teardown
    postgres.stop()


@pytest.fixture(scope="session")
def pg_uri(postgres_container):
    exposed_port = postgres_container.get_exposed_port(TEST_DB_PORT)
    return f"{{engine}}://{TEST_DB_USER}:{TEST_DB_PASSWORD}@localhost:{exposed_port}/{TEST_DB_NAME}"


@pytest.fixture
async def start_db_client(pg_uri):
    connection_uri = pg_uri.format(engine="postgresql+asyncpg")
    db_config = DatabaseConfig(connection_uri=connection_uri)
    DatabaseClient.start(db_config)
    yield


@pytest.fixture
async def external_connection(pg_uri):
    connection_uri = pg_uri.format(engine="postgres")
    async with create_pool(dsn=connection_uri) as db_pool:
        async with db_pool.acquire() as conn:
            yield conn
