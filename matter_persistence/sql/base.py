from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import UUID as sa_UUID
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Sqlalchemy base class.
    """

    pass


class IntID:
    """
    Integer primary key column
    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class StrID:
    """
    String/UUID primary key column.
    """

    id: Mapped[UUID] = mapped_column(sa_UUID(as_uuid=True), primary_key=True, default=uuid4(), unique=True)


class CreatedAtUpdatedAtMixin:
    """
    Created at and updated at columns of type datetime with timezone.
    """

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.utcnow())
    updated_at: Mapped[datetime] = mapped_column(  # noqa: UP007
        DateTime(timezone=True), server_default=func.utcnow()
    )


class SoftDeleteMixin:
    """
    Nullable deleted_at column.
    """

    deleted_at: Mapped[Optional[datetime]] = mapped_column(  # noqa: UP007
        DateTime(timezone=True), nullable=True
    )
