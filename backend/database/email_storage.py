# pylint: disable=invalid-name,import-outside-toplevel
"""Stockage SQLite pour les emails. Utilise l'espace utilisateur courant (multi-utilisateurs)."""
import json
import logging
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.core.models.email import (
    Email,
    EmailAddress,
    EmailAttachment,
)
from backend.database.migrations.runner import run_migrations

logger = logging.getLogger(__name__)


class SqliteStorage:
    """Stockage local SQLite pour les emails.

    Le répertoire de données (data_dir) est celui de l'espace utilisateur courant :
    chaque espace a sa propre BDD et ses propres données.
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        """Initialise le stockage.

        Args:
            data_dir: Répertoire de l'espace utilisateur (emails.db sera créé dedans).
                     Si None, utilise l'espace courant (user_space_dir).
        """
        from backend.config.user_space import get_current_user_space_dir

        self._data_dir = data_dir or get_current_user_space_dir()
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self._data_dir / "emails.db"
        self._migrate_legacy_data_if_needed()
        self._run_migrations_and_ensure_tables()

    def _migrate_legacy_data_if_needed(self) -> None:
        """Si des données existent à l'ancien emplacement, les copier dans l'espace courant."""
        from backend.config.settings import storage_settings

        if self.db_path.exists():
            return
        legacy_root = storage_settings.DATA_DIR / "emails.db"
        legacy_profiles = (
            storage_settings.DATA_DIR / "profiles" / "default" / "emails.db"
        )
        source_db = (
            legacy_root
            if legacy_root.exists()
            else (legacy_profiles if legacy_profiles.exists() else None)
        )
        if not source_db:
            return
        logger.info(
            "Migration des données vers l'espace utilisateur : %s -> %s",
            source_db,
            self.db_path,
        )
        shutil.copy2(source_db, self.db_path)
        source_dir = source_db.parent
        for token_file in source_dir.glob("tokens_*.json"):
            dest = self._data_dir / token_file.name
            if not dest.exists():
                shutil.copy2(token_file, dest)

    def _run_migrations_and_ensure_tables(self) -> None:
        """Exécute les migrations puis crée schema_version si nécessaire (nouvelle BDD)."""
        conn = sqlite3.connect(self.db_path)
        try:
            run_migrations(conn)
        finally:
            conn.close()

    def save_email(self, email: Email, provider: str = "gmail") -> bool:
        """Sauvegarde un email dans la base de données (avec la boîte d'origine)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO emails (
                    id, thread_id, subject, from_name, from_email,
                    to_addresses, cc_addresses, bcc_addresses,
                    date, body_text, body_html, attachments, labels, snippet, provider
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    provider.lower(),
                ),
            )

            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error("Erreur lors de la sauvegarde de l'email: %s", e)
            return False
        finally:
            conn.close()

    def get_emails(
        self,
        max_results: int = 50,
        offset: int = 0,
        provider_filter: str | None = None,
    ) -> tuple[list[Email], int]:
        """Retourne les emails en base (paginés). provider_filter: gmail, outlook, ou None/all."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            if provider_filter and provider_filter.lower() not in ("", "all"):
                pf = provider_filter.lower()
                cursor.execute(
                    "SELECT COUNT(*) FROM emails WHERE provider = ?", (pf,)
                )
                total = cursor.fetchone()[0]
                cursor.execute(
                    """
                    SELECT id, thread_id, subject, from_name, from_email,
                           to_addresses, cc_addresses, bcc_addresses,
                           date, body_text, body_html, attachments, labels, snippet, provider
                    FROM emails
                    WHERE provider = ?
                    ORDER BY date DESC
                    LIMIT ? OFFSET ?
                    """,
                    (pf, max_results, offset),
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM emails")
                total = cursor.fetchone()[0]
                cursor.execute(
                    """
                    SELECT id, thread_id, subject, from_name, from_email,
                           to_addresses, cc_addresses, bcc_addresses,
                           date, body_text, body_html, attachments, labels, snippet, provider
                    FROM emails
                    ORDER BY date DESC
                    LIMIT ? OFFSET ?
                    """,
                    (max_results, offset),
                )
            rows = cursor.fetchall()
        finally:
            conn.close()

        emails = [self._row_to_email(row) for row in rows]
        return emails, total

    def _row_to_email(self, row: tuple) -> Email:
        """Construit un Email métier à partir d'une ligne SQLite."""
        # pylint: disable=too-many-locals
        (
            id_,
            thread_id,
            subject,
            from_name,
            from_email,
            to_addresses_json,
            cc_addresses_json,
            bcc_addresses_json,
            date_str,
            body_text,
            body_html,
            attachments_json,
            labels_json,
            snippet,
            provider,
        ) = row

        def parse_addresses(data: str) -> list[EmailAddress]:
            if not data:
                return []
            items = json.loads(data)
            return [
                EmailAddress(email=a["email"], name=a.get("name"))
                for a in items
            ]

        def parse_attachments(data: str) -> list[EmailAttachment]:
            if not data:
                return []
            items = json.loads(data)
            return [
                EmailAttachment(
                    filename=a["filename"],
                    mime_type=a["mime_type"],
                    size=a["size"],
                    attachment_id=a["attachment_id"],
                )
                for a in items
            ]

        labels_list = json.loads(labels_json) if labels_json else []
        date_obj = datetime.fromisoformat(date_str) if date_str else datetime.now()

        return Email(
            id=id_,
            thread_id=thread_id,
            subject=subject or "",
            from_address=EmailAddress(email=from_email or "", name=from_name),
            to_addresses=parse_addresses(to_addresses_json),
            cc_addresses=parse_addresses(cc_addresses_json),
            bcc_addresses=parse_addresses(bcc_addresses_json),
            date=date_obj,
            body_text=body_text or "",
            body_html=body_html,
            attachments=parse_attachments(attachments_json),
            labels=labels_list,
            snippet=snippet,
            provider=provider if provider else None,
        )

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

    def update_last_sync_time(self) -> None:
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
