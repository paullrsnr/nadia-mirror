# pylint: disable=invalid-name
"""Adaptateur SQLite — implémentation du port EmailStorage."""
from backend.adapters.BDDProvider.sqlLite.models import Base, EmailModel, SyncMetadataModel
from backend.adapters.BDDProvider.sqlLite.sqliteStorage import SqliteStorage
from backend.adapters.BDDProvider.sqlLite.session import (
    init_engine,
    get_session,
    create_session,
    get_engine,
    dispose_engine,
)

__all__ = [
    "Base",
    "EmailModel",
    "SyncMetadataModel",
    "SqliteStorage",
    "init_engine",
    "get_session",
    "create_session",
    "get_engine",
    "dispose_engine",
]
