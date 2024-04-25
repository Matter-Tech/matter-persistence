from typing import Self, TypeVar

from pydantic import BaseModel

Model = TypeVar("Model", bound=BaseModel)


# Avoid using an ABC, as both the redis base model and sql base model inherits from other base classes
# this avoids "multiple-bases-have-instance-lay-out-conflict..."
class MatterPersistenceBaseDataType:
    """
    Class to hold base interface.
    """

    @classmethod
    def from_pydantic(cls, pydantic_type: type[Model]) -> Self:
        raise NotImplementedError

    def to_pydantic(self, pydantic_type: type[Model]) -> type[Model]:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> Self:
        raise NotImplementedError

    @classmethod
    def from_json(cls, obj: str | bytes | bytearray) -> Self:
        raise NotImplementedError

    def to_json(self) -> str | bytes | bytearray:
        raise NotImplementedError
