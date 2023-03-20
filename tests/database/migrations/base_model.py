from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from matter_persistence.database import DatabaseBaseModel


class BaseOrmModel(DatabaseBaseModel):
    __tablename__ = "migration_base_orm_model_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))
