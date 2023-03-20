from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .config import DatabaseConfig

DatabaseAsyncEngine = AsyncEngine


class DatabaseClient:
    __engine: DatabaseAsyncEngine = None
    pool_size: int = 1

    @classmethod
    def start(cls, config: DatabaseConfig):
        if cls.__engine:
            return

        kwargs = {}
        if config.pool_size:  # pragma: no cover
            cls.pool_size = config.pool_size
            kwargs.update({"pool_size": config.pool_size, "pool_recycle": 5})

        cls.__engine = create_async_engine(config.connection_uri, **kwargs)

    @classmethod
    async def stop(cls):
        if cls.__engine:
            await cls.__engine.dispose()

    @classmethod
    def destroy(cls):
        if cls.__engine:
            del cls.__engine
            cls.__engine = None

    @classmethod
    def get_engine(cls) -> DatabaseAsyncEngine:
        return cls.__engine
