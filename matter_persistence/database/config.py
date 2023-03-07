from typing import Optional
from urllib.parse import quote

from pydantic import SecretStr


def url_encode(p):
    return quote(p, safe="")


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
    ):
        self.pool_size = pool_size

        if connection_uri:
            self.connection_uri = connection_uri
            return

        self.connection_uri = (
            f"{engine}://"
            f"{url_encode(username.get_secret_value())}:{url_encode(password.get_secret_value())}"
            f"@{url_encode(host)}:{url_encode(str(port))}"
            f"/{url_encode(dbname)}"
        )
