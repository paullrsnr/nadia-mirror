# pylint: disable=invalid-name
"""Service d'authentification OAuth par provider (Gmail, Outlook)."""
from backend.core.models.Email import Provider
from backend.core.exceptions import ProviderError
from backend.core.models.Auth import AuthIdentity
from backend.ports.oauthPort import OAuthPort
from backend.ports.credentialGateway import CredentialGateway


class AuthService:
    """Orchestre les flux OAuth : génération d'URL, callback, statut, déconnexion.

    Les dépendances (ports OAuth et gateway credentials) sont injectées depuis la couche API.
    Le core ne sait rien de Google, de Microsoft ni du stockage des tokens.
    """

    def __init__(
        self,
        oauth_ports: dict[str, OAuthPort],
        credential_gateway: CredentialGateway,
    ) -> None:
        self._oauth_ports = oauth_ports
        self._credentials = credential_gateway

    def _get_port(self, provider: str) -> OAuthPort:
        port = self._oauth_ports.get(provider)
        if not port:
            raise ProviderError(f"Provider non supporté : {provider!r}")
        return port

    def get_auth_url(self, provider: str) -> str:
        """Génère l'URL d'autorisation OAuth2 pour le provider."""
        return self._get_port(provider).generate_auth_url(state=provider)

    def process_callback(self, code: str, provider: str) -> None:
        """Échange le code OAuth contre des tokens et sauvegarde les credentials."""
        credentials = self._get_port(provider).exchange_code(code)
        self._credentials.save(provider, credentials)

    def get_auth_status(self, provider: str) -> AuthIdentity:
        """Retourne l'identité auth pour le provider (ou toutes les boîtes si 'all')."""
        if provider == Provider.ALL.value:
            return self._get_all_status()

        credentials = self._credentials.load(provider)
        if not credentials:
            return AuthIdentity(is_authenticated=False)

        user_email = self._get_port(provider).get_user_email(credentials)
        return AuthIdentity(is_authenticated=True, email=user_email)

    def logout(self, provider: str) -> None:
        """Supprime les credentials du provider (déconnexion)."""
        self._credentials.clear(provider)

    def _get_all_status(self) -> AuthIdentity:
        email = None
        for provider in (Provider.GMAIL.value, Provider.OUTLOOK.value):
            credentials = self._credentials.load(provider)
            if not credentials:
                continue
            port = self._oauth_ports.get(provider)
            if not port:
                continue
            user_email = port.get_user_email(credentials)
            if user_email:
                email = user_email
                break

        if not email:
            return AuthIdentity(is_authenticated=False)
        return AuthIdentity(is_authenticated=True, email=email)
