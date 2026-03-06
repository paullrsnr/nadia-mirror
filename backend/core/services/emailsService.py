from backend.core.providers import (
    CONNECTABLE_PROVIDERS,
    DEFAULT_PROVIDER,
    MSG_UNAUTHENTICATED,
    MSG_INVALID_PROVIDER,
    MSG_PROVIDER_REQUIRED,
)
from backend.core.exceptions import AuthError, ProviderError
from backend.core.models.Email import ArchiveResult
from backend.ports.emailProviderGateway import EmailProviderGateway
from backend.ports.credentialGateway import CredentialGateway


class EmailsService:
    def __init__(
        self,
        email_provider_gateway: EmailProviderGateway,
        credential_gateway: CredentialGateway,
    ) -> None:
        self._email_provider_gateway = email_provider_gateway
        self._credentials = credential_gateway

    def _normalize_provider(self, provider: str | None, default: str = DEFAULT_PROVIDER) -> str:
        return (provider or "").strip().lower() or default

    def archive_email(self, email_id: str, provider: str | None) -> ArchiveResult:
        normalized = self._normalize_provider(provider)
        if normalized not in CONNECTABLE_PROVIDERS:
            raise ProviderError(MSG_PROVIDER_REQUIRED)

        credentials = self._credentials.load(normalized)
        if not credentials:
            raise AuthError(MSG_UNAUTHENTICATED)

        adapter = self._create_adapter(normalized)
        success = adapter.archive_email(email_id)

        return ArchiveResult(
            status="success" if success else "error",
            email_id=email_id,
        )

    def _create_adapter(self, provider: str):
        return self._email_provider_gateway.create(provider)
