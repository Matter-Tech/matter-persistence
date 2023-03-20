import importlib
import os
from inspect import getmembers
from typing import Callable

from alembic.config import Config

from matter_persistence.database import DatabaseBaseModel
from matter_persistence.database import (
    get_or_reuse_connection,
    DatabaseConfig,
    InvalidDatabaseConfigurationError,
    DatabaseClient,
)

from .exceptions import NotSubclassDatabaseBaseModelError, InvalidProjectConfigurationError


async def async_to_sync(func: Callable, db_config: DatabaseConfig, **kwargs):
    if not db_config.migration:
        raise InvalidDatabaseConfigurationError("The migration configuration is not set.")

    if not os.path.exists(db_config.migration.path):
        raise InvalidDatabaseConfigurationError(f"The migration folder {db_config.migration.path} does not exist.")

    script_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
    versions_dir = db_config.migration.path

    config = Config()

    config.set_main_option("file_template", db_config.migration.file_template)
    config.set_main_option("script_location", script_dir)
    config.set_main_option("version_locations", versions_dir)
    config.attributes["db_config"] = db_config

    DatabaseClient.start(db_config)

    async with get_or_reuse_connection() as async_connection:
        await async_connection.run_sync(func, config, **kwargs)


def load_db_config(module_name: str) -> DatabaseConfig:
    module = importlib.import_module(module_name)
    for i in getmembers(module, lambda x: isinstance(x, DatabaseConfig)):
        return i[1]
    else:
        raise InvalidProjectConfigurationError(f"Could not find a DatabaseConfig instance in {module_name}.")


def load_DatabaseBaseModel_subclass(full_qualified_class_path: str):
    module_path, class_name = full_qualified_class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    class_obj = getattr(module, class_name)
    if issubclass(class_obj, DatabaseBaseModel):
        return class_obj
    raise NotSubclassDatabaseBaseModelError(f"{full_qualified_class_path} is not a valid DatabaseBaseModel's subclass.")
