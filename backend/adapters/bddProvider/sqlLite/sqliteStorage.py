import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import select, func

from backend.core.models.email import Provider, Email
from backend.core.categories import EMAIL_CATEGORIES
from backend.config.settings import storage_settings
from backend.ports.emailStorage import EmailStorage
from backend.ports.settingsStorage import SettingsStorage
from backend.adapters.bddProvider.sqlLite.models import Base, CategoryModel, EmailModel, SettingModel, SyncMetadataModel
from backend.adapters.bddProvider.sqlLite.session import init_engine, create_session, get_engine
from backend.adapters.bddProvider.sqlLite import emailMapper

logger = logging.getLogger(__name__)

_SYNC_ROW_ID = 1


class SqliteStorageAdapter(EmailStorage, SettingsStorage):

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
        self._seed_categories()

    def _seed_categories(self) -> None:
        session = create_session()
        try:
            for name in EMAIL_CATEGORIES:
                exists = session.execute(
                    select(CategoryModel).where(CategoryModel.name == name)
                ).scalar_one_or_none()
                if not exists:
                    session.add(CategoryModel(name=name))
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _resolve_category_id(self, session, category_name: str) -> Optional[int]:
        row = session.execute(
            select(CategoryModel).where(CategoryModel.name == category_name)
        ).scalar_one_or_none()
        return row.id if row else None

    # ------------------------------------------------------------------ emails

    def upsert_email(self, email: Email, provider: str) -> bool:
        session = create_session()
        try:
            existing = session.get(EmailModel, email.id)
            is_new = existing is None
            model = emailMapper.to_model(email, provider)
            if existing is not None:
                model.category_id = existing.category_id
                if existing.draft_reply is not None:
                    model.draft_reply = existing.draft_reply
                model.is_archived = existing.is_archived
                model.pending_archive = existing.pending_archive
            session.merge(model)
            session.commit()
            return is_new
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def upsert_emails_batch(self, emails: list[Email], provider: str) -> list[str]:
        if not emails:
            return []
        session = create_session()
        try:
            new_ids: list[str] = []
            ids = [e.id for e in emails]
            existing_ids = {
                row for (row,) in session.execute(
                    select(EmailModel.id).where(EmailModel.id.in_(ids))
                ).all()
            }
            existing_models = {
                row.id: row for row in session.execute(
                    select(EmailModel).where(EmailModel.id.in_(existing_ids))
                ).scalars().all()
            } if existing_ids else {}

            for email in emails:
                model = emailMapper.to_model(email, provider)
                existing = existing_models.get(email.id)
                if existing is not None:
                    model.category_id = existing.category_id
                    if existing.draft_reply is not None:
                        model.draft_reply = existing.draft_reply
                    model.is_archived = existing.is_archived
                    model.pending_archive = existing.pending_archive
                else:
                    new_ids.append(email.id)
                session.merge(model)

            session.commit()
            return new_ids
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
            query = select(EmailModel).where(EmailModel.is_archived == False)  # noqa: E712
            count_query = select(func.count(EmailModel.id)).where(EmailModel.is_archived == False)  # noqa: E712, pylint: disable=not-callable

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

    def find_email_by_id(self, email_id: str) -> Optional[Email]:
        session = create_session()
        try:
            model = session.get(EmailModel, email_id)
            return emailMapper.to_domain(model) if model else None
        finally:
            session.close()

    def update_email_category(self, email_id: str, category_name: str) -> bool:
        session = create_session()
        try:
            model = session.get(EmailModel, email_id)
            if model is None:
                return False
            model.category_id = self._resolve_category_id(session, category_name)
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
                .where(EmailModel.category_id.is_(None))
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

    def update_email_draft(self, email_id: str, draft: str) -> bool:
        session = create_session()
        try:
            model = session.get(EmailModel, email_id)
            if model is None:
                return False
            model.draft_reply = draft
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def archive_email_locally(self, email_id: str) -> bool:
        session = create_session()
        try:
            model = session.get(EmailModel, email_id)
            if model is None:
                return False
            model.is_archived = True
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def set_pending_archive(self, email_id: str, pending: bool) -> bool:
        session = create_session()
        try:
            model = session.get(EmailModel, email_id)
            if model is None:
                return False
            model.pending_archive = pending
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

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

    # --------------------------------------------------------------- sync meta

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

    # ------------------------------------------------------------ categories

    def get_categories(self) -> list[dict]:
        session = create_session()
        try:
            rows = session.execute(select(CategoryModel).order_by(CategoryModel.id)).scalars().all()
            return [{"id": r.id, "name": r.name} for r in rows]
        finally:
            session.close()

    # --------------------------------------------------------------- settings

    def get_setting(self, key: str) -> str | None:
        session = create_session()
        try:
            row = session.get(SettingModel, key)
            return row.value if row else None
        finally:
            session.close()

    def set_setting(self, key: str, value: str) -> None:
        session = create_session()
        try:
            session.merge(SettingModel(key=key, value=value))
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ----------------------------------------------------------------- legacy

    def _migrate_if_needed(self) -> None:
        if self.db_path.exists():
            return
        legacy = storage_settings.DATA_DIR / "user_spaces" / "default" / "emails.db"
        if legacy.exists():
            logger.info("Migration DB legacy : %s → %s", legacy, self.db_path)
            shutil.copy2(legacy, self.db_path)
