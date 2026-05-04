from backend.core.providers import (
    CONNECTABLE_PROVIDERS,
)
from backend.core.models.email import ArchiveResult
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