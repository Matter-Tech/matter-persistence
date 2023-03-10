from pydantic import SecretStr

from matter_persistence.database import DatabaseConfig


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
