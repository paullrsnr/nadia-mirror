from datetime import datetime
from typing import Optional

from sqlalchemy import select, func

from backend.core.models.email import Provider, Email
from backend.core.models.email.category import Category
from backend.core.models.idName import IdName
from backend.adapters.bddProvider.sqlLite.models import (
    CategoryModel,
    EmailModel,
    SettingModel,
    SyncMetadataModel,
)
from backend.adapters.bddProvider.sqlLite.session import create_session
from backend.adapters.bddProvider.sqlLite import emailMapper

_SYNC_ROW_ID = 1


class SqliteReadRepository:
    """Côté lecture : requêtes emails, catégories, settings et métadonnées de sync."""

    def __init__(self) -> None:
        self._category_ids = {c.name: c.id for c in self._load_category_ids()}

    def _load_category_ids(self) -> list[IdName]:
        session = create_session()
        try:
            rows = session.execute(select(CategoryModel)).scalars().all()
            return [IdName(id=row.id, name=row.name) for row in rows]
        finally:
            session.close()

    def resolve_category_id(self, category_name: str) -> int | None:
        return self._category_ids.get(category_name)


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

    def find_emails_by_thread_id(self, thread_id: str) -> list[Email]:
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


    def get_last_sync_time(self) -> Optional[datetime]:
        session = create_session()
        try:
            row = session.get(SyncMetadataModel, _SYNC_ROW_ID)
            if row and row.last_sync_time:
                return datetime.fromisoformat(row.last_sync_time)
            return None
        finally:
            session.close()


    def get_categories(self) -> list[Category]:
        return [
            Category(id=cid, name=name)
            for name, cid in sorted(self._category_ids.items(), key=lambda x: x[1])
        ]


    def get_setting(self, key: str) -> str | None:
        session = create_session()
        try:
            row = session.get(SettingModel, key)
            return row.value if row else None
        finally:
            session.close()
