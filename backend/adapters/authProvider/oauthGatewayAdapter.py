from typing import Any

from backend.core.exceptions import ProviderError
from backend.core.models.email import Provider
from backend.ports.oauthGateway import OAuthGateway
from backend.adapters.authProvider.GMAIL.gmailOAuthAdapter import (
    generate_gmail_auth_url,
    exchange_gmail_code_for_credentials,
    get_gmail_user_email,
)
from backend.adapters.authProvider.Outlook.outlookOAuthAdapter import (
    generate_outlook_auth_url,
    get_outlook_tokens,
    get_outlook_user_email,
)


class OAuthGatewayAdapter(OAuthGateway):
    def generate_auth_url(self, provider: str, state: str) -> str:
        if provider == Provider.GMAIL.value:
            return generate_gmail_auth_url(state)
        if provider == Provider.OUTLOOK.value:
            return generate_outlook_auth_url(state)
        raise ProviderError(f"Provider OAuth non supporté : {provider!r}")

    def exchange_code(self, provider: str, code: str) -> Any:
        if provider == Provider.GMAIL.value:
            return exchange_gmail_code_for_credentials(code)
        if provider == Provider.OUTLOOK.value:
            return get_outlook_tokens(code)
        raise ProviderError(f"Provider OAuth non supporté : {provider!r}")

    def get_user_email(self, provider: str, credentials: Any) -> str | None:
        if provider == Provider.GMAIL.value:
            return get_gmail_user_email(credentials)
        if provider == Provider.OUTLOOK.value:
            return get_outlook_user_email(credentials)
        return None
