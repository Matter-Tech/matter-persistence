# matter-persistence

[![PyPI - Version](https://img.shields.io/pypi/v/matter-persistence.svg)](https://pypi.org/project/matter-persistence)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/matter-persistence.svg)](https://pypi.org/project/matter-persistence)

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install matter-persistence
```

## Usage

### SQL

Create DatabaseSessionManager instance:

```python
from matter_persistence.sql.sessions import DatabaseSessionManager

database_session_manager = DatabaseSessionManager(host="localhost")
```

Get a Connection (https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Connection):

```python
from sqlalchemy import text

async def main():
    async with database_session_manager.connect() as conn:
        await conn.execute(text("SELECT 1")).scalar()
```

Get a session (https://docs.sqlalchemy.org/en/20/orm/session_basics.html):

```python
from sqlalchemy import text, select

async def main():
    async with database_session_manager.session() as session:
        res = await session.execute(select(SomeORM))
    return res.all()
```
### Redis

Create ApiCacheClient instance:

```python
from matter_persistence.redis.api_cache_client import APICacheClient

api_cache_client = APICacheClient(host="localhost", port=6793)
```

Cache value:

```python
async def main():
    await api_cache_client.save_raw('some_key', some_pydantic_object, SomePydanticObjectClass)
```

Get value from cache:

```python
async def main():
    await api_cache_client.find_raw('some_key', SomePydanticObjectClass)
```

## Contributing

for contributions, check the [CONTRIBUTING.md](CONTRIBUTING.md) file
