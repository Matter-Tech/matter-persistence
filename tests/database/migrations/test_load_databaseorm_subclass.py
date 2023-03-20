import pytest

from matter_persistence.database.migrations.exceptions import NotSubclassDatabaseBaseModelError
from matter_persistence.database.migrations.utils import load_DatabaseBaseModel_subclass


class AnotherClass:
    pass


def test_can_load_subclass():
    loaded_class = load_DatabaseBaseModel_subclass(f"{__package__}.base_model.BaseOrmModel")
    assert loaded_class.__name__ == "BaseOrmModel"


def test_load_subclass_throws_exception_when_argument_is_not_a_subclass():
    """Test The package does not contain a DatabaseConfig instance."""
    with pytest.raises(NotSubclassDatabaseBaseModelError):
        load_DatabaseBaseModel_subclass(f"{__name__}.AnotherClass")
