# pylint: disable=invalid-name
"""Modèles SQLAlchemy pour la base de données."""
from backend.adapters.BDDProvider.sqlLite.models.base import Base
from backend.adapters.BDDProvider.sqlLite.models.emailModel import EmailModel
from backend.adapters.BDDProvider.sqlLite.models.syncMetadataModel import SyncMetadataModel

__all__ = ["Base", "EmailModel", "SyncMetadataModel"]
