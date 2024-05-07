from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from pydantic import BaseModel

from matter_persistence.foundation_model import FoundationModel

Model = TypeVar("Model", bound=BaseModel)


class CacheRecordModel(FoundationModel):
    internal_id: str
    hash_key: str
    organization_id: UUID
    value: type[BaseModel] | Any
    expiration: datetime | None = None
