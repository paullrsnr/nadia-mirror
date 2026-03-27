from abc import ABC, abstractmethod

from google.oauth2.credentials import Credentials
from backend.adapters.authProvider.Outlook.outlookTokens import OutlookTokens


class CredentialGateway(ABC):

    @abstractmethod
    def load(self, provider: str) -> Credentials | OutlookTokens | None:
        """Charge les credentials pour le provider donné."""

    @abstractmethod
    def save(self, provider: str, credentials: Credentials | OutlookTokens) -> None:
        """Sauvegarde les credentials pour le provider donné."""

    @abstractmethod
    def clear(self, provider: str) -> None:
        """Supprime les credentials pour le provider donné."""
