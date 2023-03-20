import itertools

import pytest
from pydantic import SecretStr

from matter_persistence.database import DatabaseConfig
from matter_persistence.database.config import build_connection_uri
from matter_persistence.database.exceptions import InvalidDatabaseConfigurationError


def test_config_connection_uri():
    """
    It should properly construct URI from Secrets Manager response JSON.
    """

    uri = DatabaseConfig(
        engine="sqlite",
        username=SecretStr("a-db-user"),
        password=SecretStr("wow what a safe password!!!! :))"),
        host="example.org",
        port=5432,
        dbname="a-db-name",
    ).connection_uri

    assert (
        uri == "sqlite://a-db-user:wow%20what%20a%20safe%20password%21%21%21%21%20%3A%29%29@example.org:5432/a-db-name"
    )


def test_config_connection_uri_argument_takes_precedence_over_other_args():
    """
    It should properly construct URI from Secrets Manager response JSON.
    """

    uri = DatabaseConfig(
        engine="sqlite",
        username=SecretStr("a-db-user"),
        password=SecretStr("wow what a safe password!!!! :))"),
        host="example.org",
        port=5432,
        dbname="a-db-name",
        connection_uri="i-m-the-chosen-one",
    ).connection_uri

    assert uri == "i-m-the-chosen-one"


def test_config_only_with_connection_uri():
    """
    It should properly construct URI from Secrets Manager response JSON.
    """

    uri = DatabaseConfig(
        connection_uri="i-m-alone",
    ).connection_uri

    assert uri == "i-m-alone"


@pytest.mark.parametrize(
    "engine,username,password,host,port,dbname", list(itertools.product([None, "", "a-valid-string"], repeat=6))[:-1]
)
def test_config_raises_invalid_configuration_when_no_argument_is_defined(
    engine, username, password, host, port, dbname
):
    """
    Testing that all invalid values in any position leads to exception.
    We skip the last case where all arguments are valid.
    """
    with pytest.raises(InvalidDatabaseConfigurationError):
        build_connection_uri(engine, username, password, host, port, dbname)
