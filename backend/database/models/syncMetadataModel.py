# pylint: disable=invalid-name
"""Modèle SQLAlchemy pour les métadonnées de synchronisation."""
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.models.base import Base


class SyncMetadataModel(Base):
    """Modèle de la table sync_metadata en base de données.
    
    Stocke les informations de synchronisation (timestamp, compteur).
    """
    __tablename__ = "sync_metadata"

    # Colonnes
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_sync_time: Mapped[str] = mapped_column(String, nullable=False)  # ISO format
    sync_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"SyncMetadataModel(id={self.id!r}, last_sync_time={self.last_sync_time!r}, sync_count={self.sync_count!r})"
