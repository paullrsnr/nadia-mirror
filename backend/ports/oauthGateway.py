from abc import ABC, abstractmethod

from google.oauth2.credentials import Credentials
from backend.adapters.authProvider.Outlook.outlookTokens import OutlookTokens


class OAuthGateway(ABC):

    @abstractmethod
    def generate_auth_url(self, provider: str, state: str) -> str:
        """Génère l'URL d'autorisation OAuth pour le provider donné."""

    @abstractmethod
    def exchange_code(self, provider: str, code: str, state: str) -> Credentials | OutlookTokens:
        """Échange le code de callback contre des credentials pour le provider donné."""

    @abstractmethod
    def get_user_email(self, provider: str, credentials: Credentials | OutlookTokens) -> str | None:
        """Récupère l'email utilisateur depuis les credentials du provider donné."""
