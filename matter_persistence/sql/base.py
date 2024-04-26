from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy_utils.models import Timestamp


class FilterOperators(Enum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    GT = ">"
    GTE = ">="
    ST = "<"
    STE = "<="


class SortMethodModel(Enum):
    ASC = "asc"
    DESC = "desc"


class Base(DeclarativeBase):
    """
    Sqlalchemy base class.
    """

    pass


class CustomBase(Base, Timestamp):
    """
    Custom Base class with id, created, updated, and deleted fields.
    """

    __abstract__ = True  # abstract concrete class

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    # soft deletion
    deleted: Mapped[Optional[datetime]] = mapped_column(  # noqa: UP007
        DateTime(timezone=True), nullable=True
    )
