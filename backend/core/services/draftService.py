import dataclasses
import logging
from datetime import datetime

from backend.core.providers import CONNECTABLE_PROVIDERS
from backend.core.exceptions import NotFoundError, ProviderError, ValidationError
from backend.core.models.email import (
    DraftEmail,
    EmailAddress,
    EmailAttachment,
    EmailListQuery,
    SaveDraftRequest,
    SendResult,
)
from backend.ports.emailProviderGateway import EmailProviderGateway
from backend.ports.emailStorage import EmailStorage
from backend.ports.attachmentStorage import AttachmentStorage
from backend.ports.credentialGateway import CredentialGateway
from backend.utils.textCleaner import normalize_string

logger = logging.getLogger(__name__)

MAX_ATTACHMENT_SIZE_BYTES = 25 * 1024 * 1024


class DraftService:
    def __init__(
        self,
        email_provider_gateway: EmailProviderGateway,
        credential_gateway: CredentialGateway,
        storage: EmailStorage,
        attachment_storage: AttachmentStorage,
    ) -> None:
        self._email_provider_gateway = email_provider_gateway
        self._credentials = credential_gateway
        self._storage = storage
        self._attachment_storage = attachment_storage

    def save_draft(self, draft_id: str, request: SaveDraftRequest) -> DraftEmail:
        draft = DraftEmail(
            id=draft_id,
            provider=request.provider,
            to_addresses=[EmailAddress(email=a) for a in request.to],
            cc_addresses=[EmailAddress(email=a) for a in request.cc],
            bcc_addresses=[EmailAddress(email=a) for a in request.bcc],
            subject=request.subject,
            body_text=request.body_text,
            body_html=request.body_html or None,
            updated_at=datetime.now(),
            in_reply_to_email_id=request.in_reply_to_email_id,
        )
        return self._storage.save_draft(draft)

    def delete_draft(self, draft_id: str) -> None:
        self._storage.delete_draft(draft_id)
        self._attachment_storage.delete_draft_attachments(draft_id)

    def list_drafts(self, provider: str | None = None) -> list[DraftEmail]:
        drafts = self._storage.find_drafts(provider)
        for draft in drafts:
            draft.attachments = self._attachment_storage.list_attachments(draft.id)
        return drafts

    def add_attachment(self, draft_id: str, filename: str, content: bytes) -> EmailAttachment:
        if len(content) > MAX_ATTACHMENT_SIZE_BYTES:
            raise ValidationError("Fichier trop volumineux (max 25 Mo).")
        return self._attachment_storage.save_attachment(draft_id, filename, content)

    def remove_attachment(self, draft_id: str, attachment_id: str) -> None:
        self._attachment_storage.delete_attachment(draft_id, attachment_id)

    def send_draft(self, draft_id: str) -> SendResult:
        draft = self._storage.find_draft_by_id(draft_id)
        if draft is None:
            raise NotFoundError(f"Brouillon introuvable : {draft_id}")

        normalized = normalize_string(draft.provider)
        if normalized not in CONNECTABLE_PROVIDERS:
            raise ProviderError(f"Provider inconnu : {draft.provider!r}")

        credentials = self._credentials.load(normalized)
        if not credentials:
            return SendResult(status="error", draft_id=draft_id)

        attachments = [
            self._attachment_storage.read_attachment(draft_id, attachment.attachment_id)
            for attachment in self._attachment_storage.list_attachments(draft_id)
        ]

        success = self._email_provider_gateway.send_email(normalized, draft, attachments)
        if success:
            self._storage.delete_draft(draft_id)
            self._attachment_storage.delete_draft_attachments(draft_id)

        return SendResult(
            status="success" if success else "error",
            draft_id=draft_id,
            provider=normalized if success else None,
        )

    def refresh_sent_folder(self, provider: str) -> None:
        try:
            sent = self._email_provider_gateway.fetch_emails(
                provider=provider,
                max_results=5,
                query=EmailListQuery(unread_only=False, sent_only=True),
            )
            sent_emails = [dataclasses.replace(e, folder="sent") for e in sent.emails]
            self._storage.upsert_emails_batch(sent_emails, provider=provider)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Rafraîchissement du dossier envoyés échoué pour %s : %s", provider, exc)
