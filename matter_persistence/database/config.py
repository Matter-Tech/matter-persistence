from typing import Optional, List
from urllib.parse import quote

from pydantic import SecretStr, BaseModel

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
        f"{url_encode(username.get_secret_value())}:{url_encode(password.get_secret_value())}"
        f"@{url_encode(host)}:{url_encode(str(port))}"
        f"/{url_encode(dbname)}"
    )


FILE_NAME_TEMPLATE = "%%(year)d%%(month).2d%%(day).2d-%%(hour).2d%%(minute).2d%%(second).2d-%%(slug)s"


class DatabaseMigrationConfig(BaseModel):
    path: str
    models: List[str]
    file_template: str = FILE_NAME_TEMPLATE


class DatabaseConfig:
    def __init__(
        self,
        engine: Optional[str] = None,
        username: Optional[SecretStr] = None,
        password: Optional[SecretStr] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        dbname: Optional[str] = None,
        pool_size: Optional[int] = None,
        connection_uri: Optional[str] = None,
        migration: DatabaseMigrationConfig | dict | None = None,
        models: List[str] | None = None,
    ):
        self.pool_size = pool_size
        self.migration = DatabaseMigrationConfig(**migration) if migration else None
        self.models = models

        if connection_uri:
            self.connection_uri = connection_uri
        else:
            self.connection_uri = build_connection_uri(engine, username, password, host, port, dbname)
