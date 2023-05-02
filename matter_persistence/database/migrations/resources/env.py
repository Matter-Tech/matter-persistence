import logging

import sqlalchemy
from alembic import context

from matter_persistence.database import DatabaseConfig, DatabaseBaseModel
from matter_persistence.database.migrations.utils import load_DatabaseBaseModel_subclass

config = context.config
db_config: DatabaseConfig = config.attributes["db_config"]

for i in db_config.migration.models:
    subclass = load_DatabaseBaseModel_subclass(i)

target_metadata = DatabaseBaseModel.metadata

has_schema_defined = bool(db_config.migration.version_schema)

context.configure(
    connection=config.attributes["connection"], target_metadata=target_metadata, include_schemas=has_schema_defined
)

with context.begin_transaction():
    if has_schema_defined:
        try:
            context.execute(f"SET search_path TO {db_config.migration.version_schema}")
        except sqlalchemy.exc.OperationalError:  # pragma: no cover
            logging.warning("Database does not support schemas changing.")
    context.run_migrations()
