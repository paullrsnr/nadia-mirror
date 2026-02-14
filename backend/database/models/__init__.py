# pylint: disable=invalid-name
"""Modèles SQLAlchemy pour la base de données."""
from backend.database.models.base import Base
from backend.database.models.emailModel import EmailModel
from backend.database.models.syncMetadataModel import SyncMetadataModel

__all__ = ["Base", "EmailModel", "SyncMetadataModel"]
