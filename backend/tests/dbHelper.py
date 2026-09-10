"""Outils communs aux tests qui utilisent une vraie base SQLite."""
from pathlib import Path

from backend.adapters.bddProvider.sqlLite import SqliteStorageAdapter
from backend.adapters.bddProvider.sqlLite.models.base import Base
from backend.adapters.bddProvider.sqlLite.session import dispose_engine, get_engine, init_engine


def create_test_storage(data_dir: Path) -> SqliteStorageAdapter:
    """Crée les tables (en prod, Alembic s'en charge) puis construit le stockage."""
    init_engine(data_dir / "emails.db")
    Base.metadata.create_all(get_engine())
    dispose_engine()
    return SqliteStorageAdapter(data_dir=data_dir)
