import asyncio

import pytest


@pytest.fixture(scope="session")
def event_loop():
    """
    Scope event_loop fixture to the same as db_client, i.e. scope to session.

    If we do not scope the event_loop to the same as the db_client, then the client exists
    across multiple event loops, which will break.
    """

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.run_until_complete(asyncio.sleep(0.1))
    loop.close()
