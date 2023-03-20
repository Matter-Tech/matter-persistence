import asyncio

import typer
from alembic import command
from alembic.config import Config
from sqlalchemy import Connection

from .utils import async_to_sync, load_db_config

CONFIG_MODULE_HELP = """The full qualified module name where project's DatabaseConfig
has been configured. For example: my_service.main or my_service.main.config.database"""

app = typer.Typer()


def create_database_migration(connection: Connection, config: Config, message: str):
    config.attributes["connection"] = connection
    command.revision(config, message=message, autogenerate=True)


def apply_database_migration(connection: Connection, config: Config):
    config.attributes["connection"] = connection
    command.upgrade(config, revision="head")


@app.command()
def apply(config: str = typer.Option(..., help=CONFIG_MODULE_HELP, min=1, max=1)):
    """
    Command to apply the migrations

    :param config: The full qualified module name where project's DatabaseConfig has been configured.
    """
    db_config = load_db_config(config)
    asyncio.run(async_to_sync(apply_database_migration, db_config))


@app.command()
def create(
    config: str = typer.Option(..., help=CONFIG_MODULE_HELP, min=1, max=1),
    message: str = typer.Option(..., help="The message to be used for the migration", min=1, max=1),
):
    """
    Command to create new migrations

    :param config: The full qualified module name where project's DatabaseConfig has been configured.
    :param message: The message to be used for the migration. It will be slugified and compose the migration file name.
    """
    db_config = load_db_config(config)
    asyncio.run(async_to_sync(create_database_migration, db_config, message=message))


if __name__ == "__main__":  # pragma: no cover
    app()
