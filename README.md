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

**CacheManager** and **DatabaseManager** are the two central objects in matter_persistence.

**CacheManager** encapsulates a connection pool to Redis, and exposes methods to save, retrieve, and delete values from Redis.

*Check usage example for redis* **CacheManager** *in [examples/redis](./examples/redis.ipynb).*

**DatabaseManager** encapsulates a Sqlalchemy connection pool to a relational database (e.g. Postgresql),
and exposes methods to obtain
a [Connection](https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Connection) or
a [Session](https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session).

Furthermore, there is a **CustomBase** in matter_persistence/sql/base.py, which is a convenient Base class for Sqlalchemy
ORM classes. It has an "id" primary key field, which is of type UUID, a "created", "updated" field that is inherited
from sqlalchemy_utils' Timestamp, and a "deleted" field, which is of type nullable timezone aware DateTime.

The **get** and **find** functions in matter_persistence/sql/utils.py
assume a deleted field!

*Check usage example for* **DatabaseManager** *and some of the utility functions in [examples/sql](./examples/sql.ipynb).*

## Contributing

for contributions, check the [CONTRIBUTING.md](CONTRIBUTING.md) file

