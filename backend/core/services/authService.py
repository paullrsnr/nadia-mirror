from backend.core.models.Email import Provider
from backend.core.models.Auth import AuthIdentity
from backend.ports.oauthGateway import OAuthGateway
from backend.ports.credentialGateway import CredentialGateway


class AuthService:
    def __init__(
        self,
        oauth_gateway: OAuthGateway,
        credential_gateway: CredentialGateway,
    ) -> None:
        self._oauth = oauth_gateway
        self._credentials = credential_gateway

    def get_auth_url(self, provider: str) -> str:
        return self._oauth.generate_auth_url(provider, state=provider)

    def process_callback(self, code: str, provider: str) -> None:
        credentials = self._oauth.exchange_code(provider, code)
        self._credentials.save(provider, credentials)

    def get_auth_status(self, provider: str) -> AuthIdentity:
        if provider == Provider.ALL.value:
            return self._get_all_status()
        credentials = self._credentials.load(provider)
        if not credentials:
            return AuthIdentity(is_authenticated=False)
        user_email = self._oauth.get_user_email(provider, credentials)
        return AuthIdentity(is_authenticated=True, email=user_email)

    def logout(self, provider: str) -> None:
        self._credentials.clear(provider)

    def _get_all_status(self) -> AuthIdentity:
        for provider in (Provider.GMAIL.value, Provider.OUTLOOK.value):
            credentials = self._credentials.load(provider)
            if not credentials:
                continue
            user_email = self._oauth.get_user_email(provider, credentials)
            if user_email:
                return AuthIdentity(is_authenticated=True, email=user_email)
        return AuthIdentity(is_authenticated=False)
