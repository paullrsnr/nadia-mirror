# pylint: disable=invalid-name
"""Services pour la gestion de la base de données.

- EmailRepository : Repository pattern pour les opérations CRUD
- SqliteStorage : Facade de haut niveau pour le stockage des emails
"""
from backend.database.services.emailRepository import EmailRepository
from backend.database.services.sqliteStorage import SqliteStorage

__all__ = ["EmailRepository", "SqliteStorage"]
