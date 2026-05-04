# pylint: disable=too-few-public-methods
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.adapters.bddProvider.sqlLite.models.base import Base


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"CategoryModel(id={self.id!r}, name={self.name!r})"
