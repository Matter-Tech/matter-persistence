from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from matter_persistence.database import DatabaseBaseModel

"""Having these class here for avoiding polluting the context for migrations"""


class AnotherClassToBeMigratedLater(DatabaseBaseModel):
    __tablename__ = "another_class_to_be_migrated_later"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    base_id: Mapped[int] = mapped_column(ForeignKey("migration_base_orm_model_table.id"))
    name: Mapped[str] = mapped_column(String(30))
