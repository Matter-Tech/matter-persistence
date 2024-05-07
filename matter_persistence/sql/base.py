from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Sqlalchemy base class.
    """

    pass


# this callable is used as the default value in Timestamp below
def datetime_with_utc_tz() -> datetime:
    return datetime.now(timezone.utc)  # noqa: UP017


# this is copied from sqlalchemy_utils.models.Timestamp
# datetime.utcnow is deprecated, so, until it is fixed, this copy is to be used
# it makes sense to keep sqlalchemy_utils as dependency, for example to use @generic_repr
class Timestamp:
    """Adds `created` and `updated` columns to a derived declarative model.

    The `created` column is handled through a default and the `updated`
    column is handled through a `before_update` event that propagates
    for all derived declarative models.

    ::


        import sqlalchemy as sa
        from sqlalchemy_utils import Timestamp


        class SomeModel(Base, Timestamp):
            __tablename__ = 'somemodel'
            id = sa.Column(sa.Integer, primary_key=True)
    """

    created = sa.Column(sa.DateTime(timezone=True), default=datetime_with_utc_tz, nullable=False)
    updated = sa.Column(sa.DateTime(timezone=True), default=datetime_with_utc_tz, nullable=False)


# this is copied from sqlalchemy_utils too
@sa.event.listens_for(Timestamp, "before_update", propagate=True)
def timestamp_before_update(mapper, connection, target):
    # When a model with a timestamp is updated; force update the updated
    # timestamp.
    target.updated = datetime.now(tz=timezone.utc)  # noqa: UP017


class CustomBase(Base, Timestamp):
    """
    Custom Base class with id, created, updated, and deleted fields.
    """

    __abstract__ = True  # abstract concrete class

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    # soft deletion
    deleted: Mapped[Optional[datetime]] = mapped_column(  # noqa: UP007
        DateTime(timezone=True), nullable=True, default=None
    )

    @classmethod
    def parse_dict(cls, base_model_dict: dict):
        db_model = cls()
        for key, value in base_model_dict.items():
            if hasattr(db_model, key):
                setattr(db_model, key, value)
        return db_model

    @classmethod
    def parse_obj(cls, base_model: BaseModel):
        return cls.parse_dict(base_model.model_dump())
