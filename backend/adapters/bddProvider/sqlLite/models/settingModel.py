from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text

from backend.adapters.bddProvider.sqlLite.models.base import Base


class SettingModel(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
