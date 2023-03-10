import asyncio
from contextlib import asynccontextmanager

import pytest
import sqlalchemy as sa

from matter_persistence.database import DatabaseClient, get_or_reuse_connection


def test_DatabaseClient_should_create_only_one_engine_instance(start_database_client):
    assert id(DatabaseClient.get_engine()) == id(DatabaseClient.get_engine())


@pytest.mark.asyncio
async def test_get_or_reuse_connection_should_create_different_concrete_connections(start_database_client):
    async with get_or_reuse_connection() as connection1:
        async with get_or_reuse_connection() as connection2:
            assert id(connection2) != id(connection1)


@pytest.mark.asyncio
async def test_connection_is_closed_when_leaves_the_context(start_database_client):
    async with get_or_reuse_connection() as connection:
        assert connection.closed is False
    assert connection.closed is True


@pytest.mark.asyncio
@pytest.mark.parametrize("cut_connection", [False, True])
async def test_connection_raises_error_when_reopening_a_closed_transaction(cut_connection, start_database_client):
    """
    We want to make sure that an attempt to grab a closed connection that was running some transaction raises an error.
    Otherwise, in the case of having a transaction T with steps A and B, if the connection dies during A, and B is then
    reopened as a new transaction,
    we would be saving B to the DB, even though T is incomplete without A.
    The situation is allowed to be handled gracefully, without error, if A and B are not supposed to be a transaction,
    and B can happen independently of A
    """

    try:
        async with get_or_reuse_connection(transactional=True) as connection:
            if cut_connection:
                pid = (
                    await connection.execute(sa.select(sa.func.pg_backend_pid()))
                ).scalar()  # We get the id of the connection in this transaction
                async with get_or_reuse_connection() as terminator:
                    await terminator.execute(
                        sa.select(sa.func.pg_terminate_backend(pid))
                    )  # We kill the connection in this transaction
                    await asyncio.sleep(1)

            if cut_connection is True:  # We want to test that the described scenario raises an error
                with pytest.raises(Exception):
                    async with get_or_reuse_connection(connection) as conn:
                        await conn.execute(sa.select(sa.true))
            elif (
                cut_connection is False
            ):  # We also want to test that the query runs just fine without cutting the connection,
                # proving the validity of the test setup
                async with get_or_reuse_connection(connection) as conn:
                    await conn.execute(sa.select(sa.true))
    except Exception as e:
        if cut_connection is True:
            # This is expected. The transaction context manager for "connection" does not exit nicely because we
            # killed the connection inside
            pass
        else:
            raise e


@pytest.mark.asyncio
async def test_get_or_reuse_connection_should_reuse_the_connection_in_context(start_database_client):
    async with get_or_reuse_connection() as connection1:
        async with get_or_reuse_connection(connection1) as connection2:
            assert id(connection2) == id(connection1)


@pytest.mark.asyncio
async def test_get_or_reuse_connection_reused_connection_should_isolate_transactions(start_database_client):
    async with get_or_reuse_connection() as connection1:
        async with get_or_reuse_connection(connection1) as connection2:
            async with connection2.begin() as c2t:
                assert connection2 != c2t
                assert connection2 == connection1


@pytest.mark.asyncio
async def test_get_or_reuse_connection_reuse_connection_when_open_a_transaction(start_database_client):
    async with get_or_reuse_connection() as connection1:
        async with get_or_reuse_connection(connection1, True) as connection2:
            assert connection2 == connection1


@pytest.mark.asyncio
async def test_get_or_reuse_connection_keeps_transaction_when_flag_is_not_set_when_reusing_a_transactional_connection(
    start_database_client,
):
    async with get_or_reuse_connection() as connection1:
        assert connection1.in_transaction() is False

        async with get_or_reuse_connection(connection1, True) as connection2:
            assert connection2 == connection1
            assert connection1.in_transaction() is True

            async with get_or_reuse_connection(connection2) as connection3:
                assert connection3 == connection1
                assert connection1.in_transaction() is True


@pytest.mark.asyncio
async def test_connection_is_no_longer_in_transaction_after_leaving_the_context(start_database_client):
    async with get_or_reuse_connection() as connection1:
        assert connection1.in_transaction() is False

        async with get_or_reuse_connection(connection1, True):
            assert connection1.in_transaction() is True

        # out of transactional state
        assert connection1.in_transaction() is False


@pytest.mark.asyncio
async def test_connection_is_in_nested_transaction(start_database_client):
    """
    We make sure that transactions can be nested several times with the following being true:
        - The nested transaction has new transaction context
        - The nested transaction can access database objects being processed by parent transaction(s)
        - Raising an error in a nested transaction removes that transactions items from the database for the parent
            transaction contexts
        - A successful a nested transaction does not persist to the DB if the parent/wrapping transaction(s) fail

    We do this by:
        - Creating a temporary table
        - Creating an "inner" function that creates a get_or_reuse_connection transaction context, manipulates said
            table and yields a context for further nested transactions
        - Nesting a series of transactions with the inner function
        - Assert the truths stated above, both in the deepest nesting and in the unravelling context as we through
            errors
    """

    @asynccontextmanager
    async def inner(connection, table, label, tantrum=True):
        try:
            async with get_or_reuse_connection(connection, transactional=True):  # Start a nested transaction
                assert connection.in_transaction() is True
                transaction = connection.get_nested_transaction()

                await connection.execute(sa.insert(table).values(foo=label))

                specific = (
                    await connection.execute(
                        sa.select(table.columns.foo).select_from(table).where(table.columns.foo == label)
                    )
                ).fetchall()  # Select just-inserted data

                all_ = (
                    await connection.execute(sa.select(table.columns.foo).select_from(table))
                ).fetchall()  # Select all available data

                yield connection, transaction, specific, all_  # Yield important variables and stats for nested context

                if tantrum:
                    # Throw an error to cause rollback in SQLAlchemy

                    raise RuntimeError(f"Nested transaction with label '{label}' throwing a tantrum!")

        except Exception:
            pass

    async def reasses(connection, table, items):
        # Reassess the table and assert that the table indeed has had one ore more rollbacks applied

        results = (await connection.execute(sa.select(table.columns.foo).select_from(table))).fetchall()

        assert len(results) == len(items)
        assert set([res.foo for res in results]) == items

    async with get_or_reuse_connection(transactional=False) as connection:
        table = sa.Table(
            "foo",
            sa.MetaData(),
            sa.Column("foo", sa.VARCHAR(), primary_key=True),
            prefixes=["TEMPORARY"],
        )

        await connection.execute(sa.sql.ddl.CreateTable(table))

        async with inner(connection, table, "first") as (
            _,
            trans_1,
            specific_1,
            all_1,
        ):
            async with inner(connection, table, "second") as (
                _,
                trans_2,
                specific_2,
                all_2,
            ):
                async with inner(connection, table, "third") as (
                    _,
                    trans_3,
                    specific_3,
                    all_3,
                ):
                    async with inner(connection, table, "fourth", tantrum=False) as (
                        _,
                        trans_4,
                        specific_4,
                        all_4,
                    ):
                        assert trans_1 != trans_2
                        assert trans_2 != trans_3
                        assert trans_3 != trans_4

                        assert len(specific_1) == 1
                        assert len(specific_2) == 1
                        assert len(specific_3) == 1
                        assert len(specific_4) == 1

                        assert len(all_1) == 1
                        assert len(all_2) == 2
                        assert len(all_3) == 3
                        assert len(all_4) == 4

                        assert specific_1[0]["foo"] == "first"
                        assert specific_2[0]["foo"] == "second"
                        assert specific_3[0]["foo"] == "third"
                        assert specific_4[0]["foo"] == "fourth"

                    await reasses(connection, table, {"first", "second", "third", "fourth"})
                await reasses(connection, table, {"first", "second"})
            await reasses(connection, table, {"first"})
        await reasses(connection, table, set())


async def test_get_or_reuse_connection_creating_a_nested_transaction(start_database_client):
    async with get_or_reuse_connection(transactional=True) as conn_1:
        assert conn_1.in_nested_transaction() is False
        async with get_or_reuse_connection(conn_1, transactional=True) as conn_2:
            assert conn_1.in_nested_transaction() is True
            assert conn_2 == conn_1
