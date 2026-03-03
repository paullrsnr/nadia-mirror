"""Adapter Gmail : OAuth + stockage des tokens."""
from backend.adapters.AuthProvider.GMAIL.gmailOAuthAdapter import (
    create_gmail_oauth_flow,
    generate_gmail_auth_url,
    exchange_gmail_code_for_credentials,
)
from backend.adapters.AuthProvider.GMAIL.gmailTokenStorage import (
    get_gmail_credentials,
    save_gmail_credentials,
    load_gmail_credentials,
    clear_gmail_credentials,
)

__all__ = [
    "create_gmail_oauth_flow",
    "generate_gmail_auth_url",
    "exchange_gmail_code_for_credentials",
    "get_gmail_credentials",
    "save_gmail_credentials",
    "load_gmail_credentials",
    "clear_gmail_credentials",
]
