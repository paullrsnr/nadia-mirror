# pylint: disable=invalid-name
"""Exécute les migrations du schéma. Appelé au démarrage de l'email_storage (SqliteStorage)."""
import logging
import sqlite3

from backend.database.migrations.versions import V001_initial_schema

logger = logging.getLogger(__name__)

# Liste des migrations dans l'ordre (version = index + 1)
_MIGRATIONS = [
    ("V001_initial_schema", V001_initial_schema.up),
]


def _get_schema_version(conn: sqlite3.Connection) -> int:
    """Retourne la version du schéma (0 si la table n'existe pas)."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
        )
        row = cursor.fetchone()
        return row[0] if row else 0
    except sqlite3.OperationalError:
        return 0
    finally:
        cursor.close()


def _ensure_schema_version_table(conn: sqlite3.Connection) -> None:
    """Crée la table schema_version si elle n'existe pas."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def _bootstrap_legacy(conn: sqlite3.Connection) -> None:
    """BDD existante sans table schema_version : on la met à jour et on pose version=1."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='emails'"
        )
        if not cursor.fetchone():
            return
        # Ajouter provider si manquant (anciennes BDD)
        try:
            cursor.execute(
                "ALTER TABLE emails ADD COLUMN provider TEXT DEFAULT 'gmail'"
            )
            conn.commit()
        except sqlite3.OperationalError:
            pass
        _ensure_schema_version_table(conn)
        cursor.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (1)")
        conn.commit()
    finally:
        cursor.close()


def run_migrations(conn: sqlite3.Connection) -> None:
    """Applique les migrations en attente. Gère le cas « BDD existante sans schema_version »."""
    _ensure_schema_version_table(conn)
    current = _get_schema_version(conn)

    # BDD legacy (emails existe mais version 0 car table schema_version vide)
    if current == 0:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='emails'"
            )
            if cursor.fetchone():
                _bootstrap_legacy(conn)
                current = 1
        finally:
            cursor.close()

    for i, (name, up_fn) in enumerate(_MIGRATIONS):
        version = i + 1
        if version <= current:
            continue
        logger.info("Migration %s -> version %s", name, version)
        try:
            up_fn(conn)
            conn.execute(
                "INSERT OR REPLACE INTO schema_version (version) VALUES (?)",
                (version,),
            )
            conn.commit()
        except Exception as e:
            logger.exception("Échec migration %s: %s", name, e)
            conn.rollback()
            raise
    conn.commit()
