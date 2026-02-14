"""Services pour les appels API externes (Google, Microsoft)."""
from backend.core.services.external.googleOAuthService import (
    create_gmail_oauth_flow,
    generate_gmail_auth_url,
    exchange_gmail_code_for_credentials,
)
from backend.core.services.external.googleGmailApiService import (
    get_user_email_address as get_gmail_user_email,
    build_gmail_service,
)
from backend.core.services.external.microsoftGraphService import (
    generate_outlook_auth_url,
    exchange_outlook_code_for_tokens,
    get_user_email_address as get_outlook_user_email,
)

__all__ = [
    # Google OAuth
    "create_gmail_oauth_flow",
    "generate_gmail_auth_url",
    "exchange_gmail_code_for_credentials",
    # Google Gmail API
    "get_gmail_user_email",
    "build_gmail_service",
    # Microsoft Graph
    "generate_outlook_auth_url",
    "exchange_outlook_code_for_tokens",
    "get_outlook_user_email",
]
