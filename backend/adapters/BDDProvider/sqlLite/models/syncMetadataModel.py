# pylint: disable=too-few-public-methods
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.adapters.BDDProvider.sqlLite.models.base import Base


class SyncMetadataModel(Base):
    __tablename__ = "sync_metadata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_sync_time: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f"SyncMetadataModel(id={self.id!r}, last_sync_time={self.last_sync_time!r})"
