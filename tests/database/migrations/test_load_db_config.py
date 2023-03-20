import pytest

from matter_persistence.database import DatabaseConfig
from matter_persistence.database.config import FILE_NAME_TEMPLATE
from matter_persistence.database.migrations.exceptions import InvalidProjectConfigurationError
from matter_persistence.database.migrations.utils import load_db_config

# to be set by the tests
GOOD_CONFIG = DatabaseConfig(
    connection_uri="sqlite+aiosqlite://",
    migration={"path": "a-path-to-the-migrations", "models": ["a.path.to.a.OrmModelClass"]},
)


def test_can_load_db_config():
    config = load_db_config(__name__)
    assert config.connection_uri == "sqlite+aiosqlite://"
    assert config.migration.path == "a-path-to-the-migrations"
    assert config.migration.models == ["a.path.to.a.OrmModelClass"]
    assert config.migration.file_template == FILE_NAME_TEMPLATE


def test_load_db_config_throws_exception_when_the_module_does_not_contain_db_config_class():
    """Test The package does not contain a DatabaseConfig instance."""
    with pytest.raises(InvalidProjectConfigurationError):
        load_db_config(__package__)
