# pylint: disable=invalid-name
"""Use case : archivage d'un email (délègue à l'adapter du provider)."""
from typing import Callable

from backend.core.providers import (
    CONNECTABLE_PROVIDERS,
    DEFAULT_PROVIDER,
    MSG_UNAUTHENTICATED,
    MSG_INVALID_PROVIDER,
    MSG_PROVIDER_REQUIRED,
)
from backend.core.exceptions import AuthError, ProviderError
from backend.core.models.Email import ArchiveResult
from backend.ports.emailProvider import EmailProvider as IEmailProvider
from backend.ports.credentialGateway import CredentialGateway


class EmailsService:
    """Archive un email via l'adapter du provider.

    L'adapter_factory est injectée depuis la couche API.
    """

    def __init__(
        self,
        adapter_factory: Callable[[str], IEmailProvider],
        credential_gateway: CredentialGateway,
    ) -> None:
        self._adapter_factory = adapter_factory
        self._credentials = credential_gateway

    def _normalize_provider(self, provider: str | None, default: str = DEFAULT_PROVIDER) -> str:
        return (provider or "").strip().lower() or default

    def archive_email(self, email_id: str, provider: str | None) -> ArchiveResult:
        """Archive l'email pour le provider donné.

        Raises:
            ProviderError: provider absent ou invalide.
            AuthError: credentials manquants.
        """
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

    def _create_adapter(self, provider: str) -> IEmailProvider:
        try:
            return self._adapter_factory(provider)
        except ValueError as e:
            raise ProviderError(MSG_INVALID_PROVIDER) from e
