"""Services de gestion des credentials OAuth par provider."""
from backend.core.services.Credentials.gmailCredentialsService import get_gmail_credentials
from backend.core.services.Credentials.outlookCredentialsService import get_outlook_credentials
from backend.core.services.Credentials.credentialsOrchestrator import (
    save_credentials,
    load_credentials,
    clear_credentials,
)

__all__ = [
    "get_gmail_credentials",
    "get_outlook_credentials",
    "save_credentials",
    "load_credentials",
    "clear_credentials",
]
