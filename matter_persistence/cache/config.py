import enum

from .exceptions import InvalidCacheConfigurationError

DEFAULT_TIMEOUT = 30  # seconds


class CacheEngine(enum.Enum):
    MEMORY = "memory"
    MEMCACHED = "memcached"


class CacheConfig:
    def __init__(
        self,
        endpoint: str | None = None,
        port: int | None = None,
        engine: CacheEngine = CacheEngine.MEMORY,
        object_expiration_time: int = DEFAULT_TIMEOUT,
    ):
        if engine != CacheEngine.MEMORY and not (endpoint and port):
            raise InvalidCacheConfigurationError("endpoint and port are required for non-memory cache engine")

        self.engine = engine
        self.object_expiration_time = object_expiration_time

        self.endpoint = endpoint
        self.port = port
