from matter_persistence.database import is_database_alive


async def test_is_database_alive_returns_false_when_database_client_has_not_been_started():
    alive = await is_database_alive()
    assert alive is False


async def test_is_database_alive_returns_true_when_database_client_has_been_started(start_database_client):
    alive = await is_database_alive()
    assert alive is True
