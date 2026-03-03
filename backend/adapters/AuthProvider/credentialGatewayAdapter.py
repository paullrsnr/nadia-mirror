# pylint: disable=invalid-name
"""Implémentation du port CredentialGateway : dispatche vers le bon token storage."""
from typing import Any

from backend.ports.credentialGateway import CredentialGateway
from backend.adapters.AuthProvider.GMAIL.gmailTokenStorage import (
    load_gmail_credentials,
    save_gmail_credentials,
    clear_gmail_credentials,
)
from backend.adapters.AuthProvider.Outlook.outlookTokenStorage import (
    load_outlook_credentials,
    save_outlook_credentials,
    clear_outlook_credentials,
)


class CredentialGatewayAdapter(CredentialGateway):
    """Dispatche les opérations de credentials vers Gmail ou Outlook selon le provider."""

    def load(self, provider: str) -> Any | None:
        if provider == "gmail":
            return load_gmail_credentials()
        if provider == "outlook":
            return load_outlook_credentials()
        return None

    def save(self, provider: str, credentials: Any) -> None:
        if provider == "gmail":
            save_gmail_credentials(credentials)
        elif provider == "outlook":
            save_outlook_credentials(credentials)

    def clear(self, provider: str) -> None:
        if provider == "gmail":
            clear_gmail_credentials()
        elif provider == "outlook":
            clear_outlook_credentials()
