import pytest
from sqlalchemy.orm import Mapped

from matter_persistence.foundation_model import FoundationModel
from matter_persistence.sql.base import CustomBase


class PersonORM(CustomBase):
    __tablename__ = "persons"

    name: Mapped[str]


class PersonClass:
    def __init__(self, name: str):
        self.name = name


class Person(FoundationModel):
    name: str


class PersonWithAge(Person):
    age: int


@pytest.fixture
def person_dto():
    return Person(name="john")
