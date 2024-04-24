import pytest

from matter_persistence.foundation_model import FoundationModel


# create a concrete class from FoundationModel
class TestFoundationModel(FoundationModel):
    test_field: int


@pytest.fixture
def test_foundation_model():
    return TestFoundationModel(test_field=1)


@pytest.fixture
def test_other_foundation_model():
    return TestFoundationModel(test_field=2)
