# pylint: disable=invalid-name
"""Stockage SQLite pour les emails."""
import json
import logging
import sqlite3
from datetime import datetime
from typing import Optional

from backend.api.schemas import Email
from backend.config.settings import settings

logger = logging.getLogger(__name__)


class SqliteStorage:
    """Stockage local SQLite pour les emails."""

    def __init__(self):
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.db_path = settings.DATA_DIR / "emails.db"
        self._init_database()

    def _init_database(self):
        """Initialise la base de données."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table des emails
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                subject TEXT,
                from_name TEXT,
                from_email TEXT,
                to_addresses TEXT,
                cc_addresses TEXT,
                bcc_addresses TEXT,
                date TEXT NOT NULL,
                body_text TEXT,
                body_html TEXT,
                attachments TEXT,
                labels TEXT,
                snippet TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table de synchronisation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_sync_time TEXT,
                sync_count INTEGER DEFAULT 0
            )
        """)

        # Index pour améliorer les performances
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_id ON emails(thread_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON emails(date)")

        conn.commit()
        conn.close()

    def save_email(self, email: Email) -> bool:
        """Sauvegarde un email dans la base de données."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO emails (
                    id, thread_id, subject, from_name, from_email,
                    to_addresses, cc_addresses, bcc_addresses,
                    date, body_text, body_html, attachments, labels, snippet
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    email.id,
                    email.thread_id,
                    email.subject,
                    email.from_address.name,
                    email.from_address.email,
                    json.dumps(
                        [{"name": a.name, "email": a.email} for a in email.to_addresses]
                    ),
                    json.dumps(
                        [{"name": a.name, "email": a.email} for a in email.cc_addresses]
                    ),
                    json.dumps(
                        [
                            {"name": a.name, "email": a.email}
                            for a in email.bcc_addresses
                        ]
                    ),
                    email.date.isoformat(),
                    email.body_text,
                    email.body_html,
                    json.dumps(
                        [
                            {
                                "filename": a.filename,
                                "mime_type": a.mime_type,
                                "size": a.size,
                                "attachment_id": a.attachment_id,
                            }
                            for a in email.attachments
                        ]
                    ),
                    json.dumps(email.labels),
                    email.snippet,
                ),
            )

            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error("Erreur lors de la sauvegarde de l'email: %s", e)
            return False
        finally:
            conn.close()

    # get_emails - À implémenter
    # get_threads - À implémenter
    # get_thread - À implémenter

    def get_last_sync_time(self) -> Optional[datetime]:
        """Récupère le timestamp de la dernière synchronisation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT last_sync_time FROM sync_metadata ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        conn.close()

        if row and row[0]:
            return datetime.fromisoformat(row[0])
        return None

    def update_last_sync_time(self):
        """Met à jour le timestamp de dernière synchronisation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO sync_metadata (last_sync_time, sync_count)
            VALUES (?, COALESCE((SELECT MAX(sync_count) FROM sync_metadata), 0) + 1)
        """,
            (datetime.now().isoformat(),),
        )

        conn.commit()
        conn.close()
