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
    context.run_migrations()
