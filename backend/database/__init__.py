# pylint: disable=invalid-name
"""Gestion de la base de données : stockage SQLite et migrations.

Structure:
- models/ : Modèles SQLAlchemy (EmailModel, SyncMetadataModel)
- services/ : Services de gestion de données (EmailRepository, SqliteStorage)
- session.py : Configuration de la session et engine SQLAlchemy
- alembic/ : Migrations gérées par Alembic
"""
from backend.database.models import Base, EmailModel, SyncMetadataModel
from backend.database.services import EmailRepository, SqliteStorage
from backend.database.session import (
    init_engine,
    get_session,
    create_session,
    get_engine,
    dispose_engine,
)

__all__ = [
    # Models
    "Base",
    "EmailModel",
    "SyncMetadataModel",
    # Services
    "EmailRepository",
    "SqliteStorage",
    # Session
    "init_engine",
    "get_session",
    "create_session",
    "get_engine",
    "dispose_engine",
]
