import json
from datetime import datetime

from sqlalchemy import select

from backend.core.models.email import Email
from backend.core.exceptions import NotFoundError
from backend.adapters.bddProvider.sqlLite.models import EmailModel, SettingModel, SyncMetadataModel
from backend.adapters.bddProvider.sqlLite.readRepository import SqliteReadRepository, _SYNC_ROW_ID
from backend.adapters.bddProvider.sqlLite.session import create_session
from backend.adapters.bddProvider.sqlLite import emailMapper


class SqliteWriteRepository:
    """Côté écriture : upserts et mutations sur emails, settings et métadonnées de sync."""

    def __init__(self, reads: SqliteReadRepository) -> None:
        self._reads = reads


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
                model.is_starred = existing.is_starred
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
                    model.is_starred = existing.is_starred
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

    def update_email_category(self, email_id: str, category_name: str) -> None:
        session = create_session()
        try:
            model = session.get(EmailModel, email_id)
            if model is None:
                raise NotFoundError(f"Email introuvable : {email_id}")
            model.category_id = self._reads.resolve_category_id(category_name)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update_email_draft(self, email_id: str, draft: str) -> None:
        session = create_session()
        try:
            model = session.get(EmailModel, email_id)
            if model is None:
                raise NotFoundError(f"Email introuvable : {email_id}")
            model.draft_reply = draft
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def archive_email_locally(self, email_id: str) -> None:
        session = create_session()
        try:
            model = session.get(EmailModel, email_id)
            if model is None:
                raise NotFoundError(f"Email introuvable : {email_id}")
            model.is_archived = True
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update_pending_archive(self, email_id: str, pending: bool) -> None:
        session = create_session()
        try:
            model = session.get(EmailModel, email_id)
            if model is None:
                raise NotFoundError(f"Email introuvable : {email_id}")
            model.pending_archive = pending
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def set_starred(self, email_id: str, starred: bool) -> None:
        session = create_session()
        try:
            model = session.get(EmailModel, email_id)
            if model is None:
                raise NotFoundError(f"Email introuvable : {email_id}")
            model.is_starred = starred
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def mark_email_read(self, email_id: str) -> None:
        session = create_session()
        try:
            model = session.get(EmailModel, email_id)
            if model is None:
                raise NotFoundError(f"Email introuvable : {email_id}")
            labels = json.loads(model.labels) if model.labels and model.labels != "null" else []
            if "UNREAD" in labels:
                labels.remove("UNREAD")
                model.labels = json.dumps(labels)
            session.commit()
        except Exception:
            session.rollback()
            raise
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
