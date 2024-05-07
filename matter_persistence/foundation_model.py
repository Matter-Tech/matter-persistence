import abc
import time
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from matter_persistence.sql.base import CustomBase


class FoundationModel(abc.ABC, BaseModel):
    created_at: datetime = Field(default=datetime.now(tz=timezone.utc), alias="createdAt")  # noqa: UP017
    created_at_timestamp: float = Field(default=time.time(), alias="createdAtTimestamp")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    @classmethod
    def parse_obj(cls, obj: Any):  # all the required fields must exist in the object that are use for initialisation
        if isinstance(obj, list):
            return [cls.parse_obj(item) for item in obj]
        elif isinstance(obj, CustomBase):  # sqlalchemy orm base class
            return cls(**obj.__dict__)
        elif isinstance(obj, BaseModel):
            return cls(**obj.model_dump())
        elif isinstance(obj, dict):
            return cls(**obj)
        else:
            return cls(**obj.__dict__)
