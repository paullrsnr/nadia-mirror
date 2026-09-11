from datetime import datetime

from backend.core.mailboxService import MailboxService
from backend.core.providers import CONNECTABLE_PROVIDERS
from backend.core.exceptions import InvalidInputError, NotFoundError, ProviderError
from backend.core.models.email import (
    DraftEmail,
    EmailAddress,
    EmailAttachment,
    SaveDraftRequest,
    SendResult,
)
from backend.ports.emailProviderGateway import EmailProviderGateway
from backend.ports.draftStorage import DraftStorage
from backend.ports.attachmentStorage import AttachmentStorage
from backend.ports.credentialGateway import CredentialGateway
from backend.utils.textCleaner import normalize_string

MAX_ATTACHMENT_SIZE_BYTES = 25 * 1024 * 1024
SENT_REFRESH_MAX_RESULTS = 5


class DraftService:
    def __init__(
        self,
        email_provider_gateway: EmailProviderGateway,
        credential_gateway: CredentialGateway,
        draft_storage: DraftStorage,
        attachment_storage: AttachmentStorage,
        mailbox_service: MailboxService,
    ) -> None:
        self._email_provider_gateway = email_provider_gateway
        self._credentials = credential_gateway
        self._drafts = draft_storage
        self._attachment_storage = attachment_storage
        self._mailbox = mailbox_service

    def save_draft(self, draft_id: str, request: SaveDraftRequest) -> DraftEmail:
        provider = normalize_string(request.provider)
        if provider not in CONNECTABLE_PROVIDERS:
            raise ProviderError(f"Provider inconnu : {request.provider!r}")

        draft = DraftEmail(
            id=draft_id,
            provider=provider,
            to_addresses=[EmailAddress(email=a) for a in request.to],
            cc_addresses=[EmailAddress(email=a) for a in request.cc],
            bcc_addresses=[EmailAddress(email=a) for a in request.bcc],
            subject=request.subject,
            body_text=request.body_text,
            body_html=request.body_html or None,
            updated_at=datetime.now(),
            in_reply_to_email_id=request.in_reply_to_email_id,
        )
        return self._drafts.save_draft(draft)

    def delete_draft(self, draft_id: str) -> None:
        self._drafts.delete_draft(draft_id)
        self._attachment_storage.delete_draft_attachments(draft_id)

    def list_drafts(self, provider: str | None = None) -> list[DraftEmail]:
        drafts = self._drafts.find_drafts(provider)
        for draft in drafts:
            draft.attachments = self._attachment_storage.list_attachments(draft.id)
        return drafts

    def add_attachment(self, draft_id: str, filename: str, content: bytes) -> EmailAttachment:
        if len(content) > MAX_ATTACHMENT_SIZE_BYTES:
            raise InvalidInputError("Fichier trop volumineux (max 25 Mo).")
        return self._attachment_storage.save_attachment(draft_id, filename, content)

    def remove_attachment(self, draft_id: str, attachment_id: str) -> None:
        self._attachment_storage.delete_attachment(draft_id, attachment_id)

    def send_draft(self, draft_id: str) -> SendResult:
        draft = self._drafts.find_draft_by_id(draft_id)
        if draft is None:
            raise NotFoundError(f"Brouillon introuvable : {draft_id}")

        credentials = self._credentials.load(draft.provider)
        if not credentials:
            return SendResult(status="error", draft_id=draft_id)

        attachments = [
            self._attachment_storage.read_attachment(draft_id, attachment.attachment_id)
            for attachment in self._attachment_storage.list_attachments(draft_id)
        ]

        success = self._email_provider_gateway.send_email(draft.provider, draft, attachments)
        if success:
            self._drafts.delete_draft(draft_id)
            self._attachment_storage.delete_draft_attachments(draft_id)

        return SendResult(
            status="success" if success else "error",
            draft_id=draft_id,
            provider=draft.provider if success else None,
        )

    def refresh_sent_folder(self, provider: str) -> None:
        self._mailbox.sync_sent_emails(provider, max_results=SENT_REFRESH_MAX_RESULTS)
