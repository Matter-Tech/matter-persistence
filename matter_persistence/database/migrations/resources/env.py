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

context.configure(connection=config.attributes["connection"], target_metadata=target_metadata)

with context.begin_transaction():
    if bool(db_config.migration.default_schema):
        try:
            context.execute(f"SET search_path TO {db_config.migration.default_schema}")
        except sqlalchemy.exc.OperationalError:  # pragma: no cover
            logging.warning("Database does not support schemas changing.")
    context.run_migrations()
