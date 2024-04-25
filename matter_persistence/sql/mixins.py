import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import UUID, DateTime
from sqlalchemy.orm import Mapped, mapped_column


class IntID:
    """
    Integer primary key column.
    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class StrID:
    """
    String/UUID primary key column.
    """

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4(), unique=True)


class SoftDeleteMixin:
    """
    Deleted at column.
    """

    # naming is consistent with sqlalchemy_utils's Timestamp mixin field names
    deleted: Mapped[Optional[datetime]] = mapped_column(  # noqa: UP007
        DateTime(timezone=True), nullable=True
    )
