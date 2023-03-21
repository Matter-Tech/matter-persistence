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

### With migration support

```console
pip install matter-persistence[database-migration]
```

### With postgres support

```console
pip install matter-persistence[database-postgres]
```

### With cache support 

```console
pip install matter-persistence[cache]
```

### With memcached support 

```console
pip install matter-persistence[cache-memcached]
```
## Usage

First you need to configure your database.

```python
from matter_persistence.database import DatabaseConfig

db_config = DatabaseConfig(connection_uri="sqlite:///test.db")
```

Then you need start the DatabaseClient


```python
from matter_persistence.database import DatabaseConfig, DatabaseClient

db_config = DatabaseConfig(connection_uri="sqlite:///test.db")
DatabaseClient.start(db_config)
```

One now have two options:

* Create ORM models
* Use the sqlalchemy connection directly

### ORM models

```python
from matter_persistence.database import DatabaseBaseModel
from sqlalchemy import Column, Integer, String

class ExampleModel(DatabaseBaseModel):
    __tablename__ = "example"
    id = Column(Integer, primary_key=True)
    name = Column(String)

async def an_async_function():
    example = ExampleModel(name="test")
    await example.save()
```

### sqlalchemy connection directly

```python
from matter_persistence.database import get_or_reuse_connection
import  sqlalchemy as sa

async def another_sync_function():
    async with get_or_reuse_connection() as conn:
        await conn.execute(sa.text("SELECT 1"))
```

## Migrations

One may use the command `migrations` to create and apply migrations.

First you need to configure you database client:
```python
from matter_persistence.database import DatabaseConfig

db_config = DatabaseConfig(connection_uri="sqlite:///test.db",
                           migration={"path": <a path to your migrations folder>,
                                      "models": [<a list of full qualified class path of your ORM models>]})
```
If models is an empty array, or you don't have changed the models, the command will create an empty migration
and you can customize it.

Then you can use the command `migrations` to create and apply migrations. You must provide the full qualified
python path to your configuration instance

```console
migrations create --config python.path.to.your.db_config.instance --message <migration name>
```

Then apply it, You must provide the full qualified  python path to your configuration instance:
```console
migrations apply --config python.path.to.your.db_config.instance 
```
## Cache


### Contributing

for contributions, check the [CONTRIBUTING.md](CONTRIBUTING.md) file
