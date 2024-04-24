import datetime
from enum import Enum

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Float
from sqlalchemy.ext.declarative import declared_attr


class SortMethodModel(Enum):
    ASC = "asc"
    DESC = "desc"


class BaseDBModel:
    def init_fields(self):
        self.created_at = datetime.datetime.now(tz=datetime.UTC)
        self.created_at_timestamp = self.created_at.timestamp()

    def assign(self, base_model: BaseModel, update: bool = False):
        for key, value in base_model.model_dump().items():
            ignored_fields = [
                "created_at",
                "created_at_timestamp",
                "deleted_at",
                "updated_at",
            ]
            if key in ignored_fields:
                continue

            if hasattr(self, key):
                setattr(self, key, value)

            if update:
                self.updated_at = datetime.datetime.now(tz=datetime.UTC)

    def as_dict(self):
        return self.__dict__

    def soft_delete(self):
        self.deleted_at = datetime.datetime.now(tz=datetime.UTC)

    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), default=None, nullable=False)

    @declared_attr
    def created_at_timestamp(cls):
        return Column(Float, default=None, nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime(timezone=True), default=None, nullable=False)

    @declared_attr
    def deleted_at(cls):
        return Column(DateTime(timezone=True), default=None, nullable=False)

    @classmethod
    def set_update(cls):
        cls.updated_at = datetime.datetime.now(tz=datetime.UTC)

    @classmethod
    def set_delete(cls):
        cls.deleted_at = datetime.datetime.now(tz=datetime.UTC)

    @classmethod
    def parse_dict(cls, base_model_dict: dict):
        db_model = cls()
        for key, value in base_model_dict.items():
            if hasattr(db_model, key):
                setattr(db_model, key, value)

        if base_model_dict.get("created_at") is None:
            db_model.init_fields()

        return db_model

    @classmethod
    def parse_obj(cls, base_model: BaseModel):
        return cls.parse_dict(base_model.model_dump())
