from fastapi.responses import Response

from backend.core.providers import (
    CONNECTABLE_PROVIDERS,
)
from backend.core.exceptions import NotFoundError
from backend.core.models.email import ArchiveResult, StarResult, MarkReadResult, AttachmentContent
from backend.ports.emailProviderGateway import EmailProviderGateway
from backend.ports.emailStorage import EmailStorage
from backend.ports.credentialGateway import CredentialGateway
from backend.utils.textCleaner import normalize_string


class EmailsService:
    def __init__(
        self,
        email_provider_gateway: EmailProviderGateway,
        credential_gateway: CredentialGateway,
        storage: EmailStorage,
    ) -> None:
        self._email_provider_gateway = email_provider_gateway
        self._credentials = credential_gateway
        self._storage = storage

    def archive_email(self, email_id: str, provider: str | None) -> ArchiveResult:
        normalized = normalize_string(provider)
        if normalized not in CONNECTABLE_PROVIDERS:
            return ArchiveResult(status="error", email_id=email_id)

        credentials = self._credentials.load(normalized)
        if not credentials:
            return ArchiveResult(status="error", email_id=email_id)

        success = self._email_provider_gateway.archive_email(normalized, email_id)
        if success:
            self._storage.archive_email_locally(email_id)

        return ArchiveResult(
            status="success" if success else "error",
            email_id=email_id,
        )

    def star_email(self, email_id: str, starred: bool) -> StarResult:
        self._storage.set_starred(email_id, starred)
        return StarResult(status="success", email_id=email_id, is_starred=starred)

    def mark_email_read(self, email_id: str, provider: str | None) -> MarkReadResult:
        normalized = normalize_string(provider)
        if normalized not in CONNECTABLE_PROVIDERS:
            return MarkReadResult(status="error", email_id=email_id)

        credentials = self._credentials.load(normalized)
        if not credentials:
            return MarkReadResult(status="error", email_id=email_id)

        success = self._email_provider_gateway.mark_as_read(normalized, email_id)
        if success:
            self._storage.mark_email_read(email_id)

        return MarkReadResult(
            status="success" if success else "error",
            email_id=email_id,
        )

    def get_attachment(self, email_id: str, attachment_id: str) -> AttachmentContent:
        email = self._storage.find_email_by_id(email_id)
        if not email:
            raise NotFoundError(f"Email introuvable : {email_id}")

        meta = next((a for a in email.attachments if a.attachment_id == attachment_id), None)
        if not meta:
            raise NotFoundError(f"Pièce jointe introuvable : {attachment_id}")

        content = self._email_provider_gateway.get_attachment_content(
            email.provider.value, email_id, attachment_id
        )
        return AttachmentContent(filename=meta.filename, mime_type=meta.mime_type, content=content)

    def build_attachment_response(self, email_id: str, attachment_id: str) -> Response:
        attachment = self.get_attachment(email_id, attachment_id)
        return Response(
            content=attachment.content,
            media_type=attachment.mime_type or "application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{attachment.filename}"'},
        )