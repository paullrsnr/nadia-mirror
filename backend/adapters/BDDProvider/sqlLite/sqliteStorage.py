# pylint: disable=invalid-name
"""Stockage SQLite des emails (implémente EmailStorage)."""
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import select, func

from backend.core.models.Email import Provider
from backend.config.settings import storage_settings
from backend.core.models.Email import Email, EmailAddress, EmailAttachment
from backend.ports.emailStorage import EmailStorage
from backend.adapters.BDDProvider.sqlLite.models import Base, EmailModel, SyncMetadataModel
from backend.adapters.BDDProvider.sqlLite.session import init_engine, create_session, get_engine

logger = logging.getLogger(__name__)

_SYNC_ROW_ID = 1  # ligne unique dans sync_metadata


# ---------------------------------------------------------------------------
# Fonctions de mapping (module-level, sans état)
# ---------------------------------------------------------------------------

def _parse_addresses(data: str | None) -> list[EmailAddress]:
    if not data or data == "null":
        return []
    items = json.loads(data)
    return [EmailAddress(email=a["email"], name=a.get("name")) for a in items]


def _parse_attachments(data: str | None) -> list[EmailAttachment]:
    if not data or data == "null":
        return []
    items = json.loads(data)
    return [
        EmailAttachment(
            filename=a["filename"],
            mime_type=a["mime_type"],
            size=a["size"],
            attachment_id=a.get("attachment_id"),
        )
        for a in items
    ]


def _to_email(model: EmailModel) -> Email:
    labels = json.loads(model.labels) if model.labels and model.labels != "null" else []
    date = datetime.fromisoformat(model.date) if model.date else datetime.now()
    return Email(
        id=model.id,
        thread_id=model.thread_id,
        subject=model.subject or "",
        from_address=EmailAddress(email=model.from_email or "", name=model.from_name),
        to_addresses=_parse_addresses(model.to_addresses),
        cc_addresses=_parse_addresses(model.cc_addresses),
        bcc_addresses=_parse_addresses(model.bcc_addresses),
        date=date,
        body_text=model.body_text or "",
        body_html=model.body_html,
        attachments=_parse_attachments(model.attachments),
        labels=labels,
        snippet=model.snippet,
        provider=model.provider or None,
    )


def _to_model(email: Email, provider: str) -> EmailModel:
    return EmailModel(
        id=email.id,
        thread_id=email.thread_id,
        subject=email.subject,
        from_name=email.from_address.name,
        from_email=email.from_address.email,
        to_addresses=json.dumps([{"name": a.name, "email": a.email} for a in email.to_addresses]),
        cc_addresses=json.dumps([{"name": a.name, "email": a.email} for a in email.cc_addresses]),
        bcc_addresses=json.dumps([{"name": a.name, "email": a.email} for a in email.bcc_addresses]),
        date=email.date.isoformat(),
        body_text=email.body_text,
        body_html=email.body_html,
        attachments=json.dumps([
            {
                "filename": a.filename, "mime_type": a.mime_type,
                "size": a.size, "attachment_id": a.attachment_id,
            }
            for a in email.attachments
        ]),
        labels=json.dumps(email.labels),
        snippet=email.snippet,
        provider=provider.lower(),
    )


# ---------------------------------------------------------------------------
# Implémentation du port EmailStorage
# ---------------------------------------------------------------------------

class SqliteStorage(EmailStorage):
    """Stockage local SQLite pour les emails."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self._custom_data_dir = data_dir is not None
        self._data_dir = data_dir or storage_settings.DATA_DIR
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self._data_dir / "emails.db"
        if not self._custom_data_dir:
            self._migrate_if_needed()
        self._init_db()

    def _migrate_if_needed(self) -> None:
        """Copie l'ancienne BDD (user_spaces/default/) si la nouvelle n'existe pas encore."""
        if self.db_path.exists():
            return
        legacy = storage_settings.DATA_DIR / "user_spaces" / "default" / "emails.db"
        if legacy.exists():
            logger.info("Migration DB legacy : %s → %s", legacy, self.db_path)
            shutil.copy2(legacy, self.db_path)

    def _init_db(self) -> None:
        init_engine(self.db_path)
        Base.metadata.create_all(bind=get_engine())

    # --- Port EmailStorage ---

    def save_email(self, email: Email, provider: str) -> bool:
        """Sauvegarde un email. Retourne True si créé, False si déjà présent."""
        session = create_session()
        try:
            is_new = session.get(EmailModel, email.id) is None
            session.merge(_to_model(email, provider))
            session.commit()
            return is_new
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def find_emails(
        self,
        max_results: int = 50,
        offset: int = 0,
        provider_filter: str | None = None,
    ) -> tuple[list[Email], int]:
        """Retourne (emails paginés, total) depuis la BDD locale."""
        session = create_session()
        try:
            query = select(EmailModel)
            count_query = select(func.count(EmailModel.id))  # pylint: disable=not-callable

            if provider_filter and provider_filter.lower() not in ("", Provider.ALL.value):
                pf = provider_filter.lower()
                query = query.where(EmailModel.provider == pf)
                count_query = count_query.where(EmailModel.provider == pf)

            total = session.execute(count_query).scalar() or 0
            query = query.order_by(EmailModel.date.desc()).limit(max_results).offset(offset)
            emails = [_to_email(m) for m in session.execute(query).scalars().all()]
            return emails, total
        finally:
            session.close()

    def get_last_sync_time(self) -> Optional[datetime]:
        """Timestamp de la dernière synchronisation, ou None."""
        session = create_session()
        try:
            row = session.get(SyncMetadataModel, _SYNC_ROW_ID)
            if row and row.last_sync_time:
                return datetime.fromisoformat(row.last_sync_time)
            return None
        finally:
            session.close()

    def update_last_sync_time(self) -> None:
        """Met à jour (ou crée) la ligne unique de métadonnées de sync."""
        session = create_session()
        try:
            row = session.get(SyncMetadataModel, _SYNC_ROW_ID)
            count = (row.sync_count + 1) if row else 1
            session.merge(SyncMetadataModel(
                id=_SYNC_ROW_ID,
                last_sync_time=datetime.now().isoformat(),
                sync_count=count,
            ))
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
