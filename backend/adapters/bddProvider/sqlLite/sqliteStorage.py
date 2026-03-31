import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import select, func

from backend.core.models.email import Provider, Email
from backend.config.settings import storage_settings
from backend.ports.emailStorage import EmailStorage
from backend.adapters.bddProvider.sqlLite.models import Base, EmailModel, SyncMetadataModel
from backend.adapters.bddProvider.sqlLite.session import init_engine, create_session, get_engine
from backend.adapters.bddProvider.sqlLite import emailMapper

logger = logging.getLogger(__name__)

_SYNC_ROW_ID = 1  # ligne unique dans sync_metadata


class SqliteStorageAdapter(EmailStorage):

    def __init__(self, data_dir: Path | None = None) -> None:
        self._custom_data_dir = data_dir is not None
        self._data_dir = data_dir or storage_settings.DATA_DIR
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self._data_dir / "emails.db"
        if not self._custom_data_dir:
            self._migrate_if_needed()
        self._init_db()

    def _init_db(self) -> None:
        init_engine(self.db_path)
        Base.metadata.create_all(bind=get_engine())


    def save_email(self, email: Email, provider: str) -> bool:
        session = create_session()
        try:
            existing = session.get(EmailModel, email.id)
            is_new = existing is None
            model = emailMapper.to_model(email, provider)
            if existing is not None and existing.category is not None:
                model.category = existing.category
            session.merge(model)
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
            emails = [emailMapper.to_domain(m) for m in session.execute(query).scalars().all()]
            return emails, total
        finally:
            session.close()

    def get_last_sync_time(self) -> Optional[datetime]:
        session = create_session()
        try:
            row = session.get(SyncMetadataModel, _SYNC_ROW_ID)
            if row and row.last_sync_time:
                return datetime.fromisoformat(row.last_sync_time)
            return None
        finally:
            session.close()

    def update_last_sync_time(self) -> None:
        session = create_session()
        try:
            row = session.get(SyncMetadataModel, _SYNC_ROW_ID)
            session.merge(SyncMetadataModel(
                id=_SYNC_ROW_ID,
                last_sync_time=datetime.now().isoformat(),
            ))
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    
    def find_email_by_id(self, email_id: str) -> Optional[Email]:
        session = create_session()
        try:
            model = session.get(EmailModel, email_id)
            return emailMapper.to_domain(model) if model else None
        finally:
            session.close()

    def update_email_category(self, email_id: str, category: str) -> bool:
        session = create_session()
        try:
            model = session.get(EmailModel, email_id)
            if model is None:
                return False
            model.category = category
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def find_uncategorized_emails(self, limit: int = 50) -> list[Email]:
        session = create_session()
        try:
            query = (
                select(EmailModel)
                .where(EmailModel.category.is_(None))
                .order_by(EmailModel.date.desc())
                .limit(limit)
            )
            return [emailMapper.to_domain(m) for m in session.execute(query).scalars().all()]
        finally:
            session.close()

    def find_emails_by_thread(self, thread_id: str) -> list[Email]:
        session = create_session()
        try:
            query = (
                select(EmailModel)
                .where(EmailModel.thread_id == thread_id)
                .order_by(EmailModel.date.asc())
            )
            return [emailMapper.to_domain(m) for m in session.execute(query).scalars().all()]
        finally:
            session.close()

    def _migrate_if_needed(self) -> None:
        if self.db_path.exists():
            return
        legacy = storage_settings.DATA_DIR / "user_spaces" / "default" / "emails.db"
        if legacy.exists():
            logger.info("Migration DB legacy : %s → %s", legacy, self.db_path)
            shutil.copy2(legacy, self.db_path)