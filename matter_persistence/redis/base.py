from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from matter_persistence.base import MatterPersistenceBaseDataType, Model


class CacheRecordModel(MatterPersistenceBaseDataType, BaseModel):
    internal_id: str
    hash_key: str
    organization_id: UUID
    value: Any
    expiration: datetime | None = None

    @classmethod
    def from_pydantic(cls, pydantic_type: type[Model]):
        return cls  # already a pydantic type

    def to_pydantic(self, pydantic_type: type[Model]):
        return self  # already a pydantic type

    @classmethod
    def from_dict(cls, d: dict, **kwargs) -> "CacheRecordModel":
        return CacheRecordModel.model_validate(d, **kwargs)

    @classmethod
    def from_json(cls, obj: str | bytes | bytearray, **kwargs) -> "CacheRecordModel":
        return CacheRecordModel.model_validate_json(obj, **kwargs)

    def to_json(self, **kwargs) -> str:
        return self.model_dump_json(**kwargs)
