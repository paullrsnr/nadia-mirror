# pylint: disable=invalid-name
"""Use case : archivage d'un email (délègue à l'adapter Gmail ou Outlook)."""
from fastapi import HTTPException

from backend.config.providers import (
    CONNECTABLE_PROVIDERS,
    DEFAULT_PROVIDER,
    MSG_UNAUTHENTICATED,
    MSG_INVALID_PROVIDER,
    MSG_PROVIDER_REQUIRED,
)
from backend.config.adapterRegistry import AdapterRegistry
from backend.core.models.Email import ArchiveResult
from backend.core.services.connection import get_connection_credentials


class EmailsService:
    """Archive un email via l'adapter du provider (Gmail ou Outlook)."""

    def _normalize_provider(self, provider: str | None, default: str = DEFAULT_PROVIDER) -> str:
        """Normalise le provider (strip, lower, fallback)."""
        return (provider or "").strip().lower() or default

    def archive_email(self, email_id: str, provider: str | None) -> ArchiveResult:
        """Archive l'email pour le provider donné et retourne le résultat."""
        normalized = self._normalize_provider(provider)
        if normalized not in CONNECTABLE_PROVIDERS:
            raise HTTPException(status_code=400, detail=MSG_PROVIDER_REQUIRED)

        credentials = get_connection_credentials(normalized)
        if not credentials:
            raise HTTPException(status_code=401, detail=MSG_UNAUTHENTICATED)

        adapter = self._create_adapter(normalized)
        success = adapter.archive_email(email_id)

        return ArchiveResult(
            status="success" if success else "error",
            email_id=email_id,
        )

    def _create_adapter(self, provider: str):
        """Crée l'adapter pour le provider (gmail ou outlook)."""
        adapter_class = AdapterRegistry.get_adapter_class(provider)
        if not adapter_class:
            raise HTTPException(status_code=400, detail=MSG_INVALID_PROVIDER)
        return adapter_class()
