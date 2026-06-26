import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import select, func

from backend.core.models.email import Provider, Email, DraftEmail
from backend.core.models.email.category import Category
from backend.config.settings import storage_settings
from backend.ports.emailStorage import EmailStorage
from backend.ports.settingsStorage import SettingsStorage
from backend.adapters.bddProvider.sqlLite.session import init_engine
from backend.adapters.bddProvider.sqlLite.readRepository import SqliteReadRepository
from backend.adapters.bddProvider.sqlLite.writeRepository import SqliteWriteRepository
from backend.adapters.bddProvider.sqlLite.models import (
    CategoryModel, EmailModel, SettingModel, SyncMetadataModel, DraftEmailModel,
)
from backend.adapters.bddProvider.sqlLite.session import init_engine, create_session
from backend.adapters.bddProvider.sqlLite import emailMapper, draftEmailMapper

logger = logging.getLogger(__name__)


class SqliteStorageAdapter(EmailStorage, SettingsStorage):
    """Façade qui compose le repository de lecture et celui d'écriture."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self._custom_data_dir = data_dir is not None
        self._data_dir = data_dir or storage_settings.DATA_DIR
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self._data_dir / "emails.db"
        if not self._custom_data_dir:
            self._migrate_if_needed()
        init_engine(self.db_path)
        self._reads = SqliteReadRepository()
        self._writes = SqliteWriteRepository(self._reads)


    def find_emails(
        self,
        max_results: int = 50,
        offset: int = 0,
        provider_filter: str | None = None,
        folder: str | None = "inbox",
    ) -> tuple[list[Email], int]:
        session = create_session()
        try:
            query = select(EmailModel).where(EmailModel.is_archived == False)  # noqa: E712
            count_query = select(func.count(EmailModel.id)).where(EmailModel.is_archived == False)  # noqa: E712, pylint: disable=not-callable

            if provider_filter and provider_filter.lower() not in ("", Provider.ALL.value):
                pf = provider_filter.lower()
                query = query.where(EmailModel.provider == pf)
                count_query = count_query.where(EmailModel.provider == pf)

            if folder is not None:
                query = query.where(EmailModel.folder == folder)
                count_query = count_query.where(EmailModel.folder == folder)

            total = session.execute(count_query).scalar() or 0
            query = query.order_by(EmailModel.date.desc()).limit(max_results).offset(offset)
            emails = [emailMapper.to_domain(m) for m in session.execute(query).scalars().all()]
            return emails, total
        finally:
            session.close()

    def find_email_by_id(self, email_id: str) -> Optional[Email]:
        return self._reads.find_email_by_id(email_id)

    def find_uncategorized_emails(self, limit: int = 50) -> list[Email]:
        return self._reads.find_uncategorized_emails(limit)

    def find_emails_by_thread_id(self, thread_id: str) -> list[Email]:
        return self._reads.find_emails_by_thread_id(thread_id)

    def find_pending_archive_emails(self) -> list[Email]:
        session = create_session()
        try:
            query = (
                select(EmailModel)
                .where(EmailModel.pending_archive == True)  # noqa: E712
                .where(EmailModel.is_archived == False)  # noqa: E712
                .order_by(EmailModel.date.desc())
            )
            return [emailMapper.to_domain(m) for m in session.execute(query).scalars().all()]
        finally:
            session.close()

    # ------------------------------------------------------------------ drafts

    def save_draft(self, draft: DraftEmail) -> DraftEmail:
        session = create_session()
        try:
            model = draftEmailMapper.to_model(draft)
            session.merge(model)
            session.commit()
            return draft
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def find_draft_by_id(self, draft_id: str) -> Optional[DraftEmail]:
        session = create_session()
        try:
            model = session.get(DraftEmailModel, draft_id)
            return draftEmailMapper.to_domain(model) if model else None
        finally:
            session.close()

    def delete_draft(self, draft_id: str) -> None:
        session = create_session()
        try:
            model = session.get(DraftEmailModel, draft_id)
            if model is not None:
                session.delete(model)
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def find_drafts(self, provider: str | None = None) -> list[DraftEmail]:
        session = create_session()
        try:
            query = select(DraftEmailModel).order_by(DraftEmailModel.updated_at.desc())
            if provider:
                query = query.where(DraftEmailModel.provider == provider)
            return [draftEmailMapper.to_domain(m) for m in session.execute(query).scalars().all()]
        finally:
            session.close()

    # --------------------------------------------------------------- sync meta

    def get_last_sync_time(self) -> Optional[datetime]:
        return self._reads.get_last_sync_time()

    def get_categories(self) -> list[Category]:
        return self._reads.get_categories()

    def get_setting(self, key: str) -> str | None:
        return self._reads.get_setting(key)


    def upsert_email(self, email: Email, provider: str) -> bool:
        return self._writes.upsert_email(email, provider)

    def upsert_emails_batch(self, emails: list[Email], provider: str) -> list[str]:
        return self._writes.upsert_emails_batch(emails, provider)

    def update_email_category(self, email_id: str, category: str) -> None:
        self._writes.update_email_category(email_id, category)

    def update_email_draft(self, email_id: str, draft: str) -> None:
        self._writes.update_email_draft(email_id, draft)

    def archive_email_locally(self, email_id: str) -> None:
        self._writes.archive_email_locally(email_id)

    def update_pending_archive(self, email_id: str, pending: bool) -> None:
        self._writes.update_pending_archive(email_id, pending)

    def set_starred(self, email_id: str, starred: bool) -> None:
        self._writes.set_starred(email_id, starred)

    def mark_email_read(self, email_id: str) -> None:
        self._writes.mark_email_read(email_id)

    def update_last_sync_time(self) -> None:
        self._writes.update_last_sync_time()

    def set_setting(self, key: str, value: str) -> None:
        self._writes.set_setting(key, value)


    def _migrate_if_needed(self) -> None:
        if self.db_path.exists():
            return
        legacy = storage_settings.DATA_DIR / "user_spaces" / "default" / "emails.db"
        if legacy.exists():
            logger.info("Migration DB legacy : %s → %s", legacy, self.db_path)
            shutil.copy2(legacy, self.db_path)
