# pylint: disable=invalid-name
"""Gestion de la base de données : stockage SQLite et migrations.

- Stockage : email_storage (SqliteStorage) pour persister les emails en SQLite.
- Migrations : exécutées au démarrage pour faire évoluer le schéma sans script manuel.
"""
from backend.database.email_storage import SqliteStorage

__all__ = ["SqliteStorage"]
