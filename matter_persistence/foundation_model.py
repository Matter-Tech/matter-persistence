import abc
import time
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from matter_persistence.sql.models import BaseDBModel


class FoundationModel(BaseModel, abc.ABC):
    created_at: datetime = Field(default=datetime.now(tz=UTC), alias="createdAt")
    created_at_timestamp: float = Field(default=time.time(), alias="createdAtTimestamp")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    @classmethod
    def parse_obj(cls, obj: Any):
        if isinstance(obj, list):
            return [cls.parse_obj(item) for item in obj]
        elif isinstance(obj, BaseDBModel):
            return cls(**obj.as_dict())
        elif isinstance(obj, BaseModel):
            return cls(**obj.model_dump())
        elif isinstance(obj, dict):
            return cls(**obj)
        else:
            return cls(**obj.__dict__)

    def assign(self, base_model: BaseModel):
        for key, value in base_model.model_dump().items():
            if hasattr(self, key):
                setattr(self, key, value)
