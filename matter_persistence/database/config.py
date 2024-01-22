from dataclasses import dataclass
from urllib.parse import quote


from .exceptions import InvalidDatabaseConfigurationError


def url_encode(p):
    return quote(p, safe="")


def build_connection_uri(engine, username, password, host, port, dbname):
    if any([not bool(opts) for opts in (engine, username, password, host, port, dbname)]):
        msg = ""
        if not bool(engine):
            msg = f'engine can\'t be "{engine}".'
        if not bool(username):
            msg = f'{msg} username can\'t be "{engine}".'
        if not bool(password):
            msg = f'{msg} password can\'t be "{engine}".'
        if not bool(host):
            msg = f'{msg} host can\'t be "{engine}".'
        if not bool(port):
            msg = f'{msg} port can\'t be "{engine}".'
        if not bool(dbname):
            msg = f'{msg} dbname can\'t be "{engine}".'
        raise InvalidDatabaseConfigurationError(f"Invalid database configuration.{msg} when connection_uri is not set.")

    return (
        f"{engine}://"
        f"{url_encode(username)}:{url_encode(password)}"
        f"@{url_encode(host)}:{url_encode(str(port))}"
        f"/{url_encode(dbname)}"
    )


FILE_NAME_TEMPLATE = "%%(year)d%%(month).2d%%(day).2d-%%(hour).2d%%(minute).2d%%(second).2d-%%(slug)s"


@dataclass
class DatabaseMigrationConfig:
    path: str
    models: list[str]
    file_template: str = FILE_NAME_TEMPLATE
    version_schema: str | None = None


class DatabaseConfig:
    def __init__(
        self,
        engine: str | None = None,
        username: str | None = None,
        password: str | None = None,
        host: str | None = None,
        port: int | None = None,
        dbname: str | None = None,
        pool_size: int | None = None,
        connection_uri: str | None = None,
        migration: DatabaseMigrationConfig | dict | None = None,
        models: list[str] | None = None,
    ):
        self.pool_size = pool_size
        self.migration = DatabaseMigrationConfig(**migration) if migration else None
        self.models = models

        if connection_uri:
            self.connection_uri = connection_uri
        else:
            self.connection_uri = build_connection_uri(engine, username, password, host, port, dbname)
