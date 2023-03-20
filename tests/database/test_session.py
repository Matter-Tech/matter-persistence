from matter_persistence.database import get_or_reuse_session


async def test_get_or_reuse_session_creating_a_nested_transaction(start_database_client):
    async with get_or_reuse_session(transactional=True) as session_1:
        assert session_1.in_nested_transaction() is False
        async with get_or_reuse_session(session_1, transactional=True) as session_2:
            assert session_1.in_nested_transaction() is True
            assert session_2 == session_1


async def test_get_or_reuse_session_can_transform_non_transaction_session_into_one(start_database_client):
    async with get_or_reuse_session() as session_1:
        assert session_1.in_transaction() is False
        async with get_or_reuse_session(session_1, transactional=True) as session_2:
            assert session_1.in_transaction() is True
            assert session_1.in_nested_transaction() is False
            assert session_2 == session_1


async def test_get_or_reuse_session_reuses_connection(start_database_client):
    async with get_or_reuse_session() as session_1:
        async with get_or_reuse_session(session_1) as session_2:
            assert session_2 == session_1
