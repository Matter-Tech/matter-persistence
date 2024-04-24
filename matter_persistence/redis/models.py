from datetime import datetime
from typing import Any
from uuid import UUID

from matter_persistence.foundation_model import FoundationModel


class CacheRecordModel(FoundationModel):
    internal_id: str
    hash_key: str
    organization_id: UUID
    value: Any
    expiration: datetime | None
