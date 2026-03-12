from typing import Any

from backend.core.models.email import Provider
from backend.ports.credentialGateway import CredentialGateway
from backend.adapters.authProvider.GMAIL.gmailTokenStorage import (
    get_gmail_credentials,
    save_gmail_credentials,
    clear_gmail_credentials,
)
from backend.adapters.authProvider.Outlook.outlookTokenStorage import (
    load_outlook_credentials,
    save_outlook_credentials,
    clear_outlook_credentials,
)

from google.oauth2.credentials import Credentials
from backend.adapters.authProvider.Outlook.outlookTokens import OutlookTokens

class CredentialGatewayAdapter(CredentialGateway):
    def load(self, provider: str) -> Credentials | OutlookTokens | None:
        if provider == Provider.GMAIL.value:
            return get_gmail_credentials()
        if provider == Provider.OUTLOOK.value:
            return load_outlook_credentials()
        return None

    def save(self, provider: str, credentials: Any) -> None:
        if provider == Provider.GMAIL.value:
            save_gmail_credentials(credentials)
        elif provider == Provider.OUTLOOK.value:
            save_outlook_credentials(credentials)

    def clear(self, provider: str) -> None:
        if provider == Provider.GMAIL.value:
            clear_gmail_credentials()
        elif provider == Provider.OUTLOOK.value:
            clear_outlook_credentials()
