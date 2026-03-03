"""Adapter Outlook : OAuth + stockage des tokens."""
from backend.adapters.AuthProvider.Outlook.outlookOAuthAdapter import (
    generate_outlook_auth_url,
    exchange_outlook_code_for_tokens,
    get_outlook_user_email,
)
from backend.adapters.AuthProvider.Outlook.outlookTokenStorage import (
    get_outlook_credentials,
    save_outlook_credentials,
    load_outlook_credentials,
    clear_outlook_credentials,
)

__all__ = [
    "generate_outlook_auth_url",
    "exchange_outlook_code_for_tokens",
    "get_outlook_user_email",
    "get_outlook_credentials",
    "save_outlook_credentials",
    "load_outlook_credentials",
    "clear_outlook_credentials",
]
