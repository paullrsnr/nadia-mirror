"""Port de stockage des credentials OAuth par provider."""
from abc import ABC, abstractmethod
from typing import Any


class CredentialGateway(ABC):
    """Contrat pour charger, sauvegarder et supprimer les credentials d'un provider OAuth."""

    @abstractmethod
    def load(self, provider: str) -> Any | None:
        """Charge les credentials pour le provider donné."""

    @abstractmethod
    def save(self, provider: str, credentials: Any) -> None:
        """Sauvegarde les credentials pour le provider donné."""

    @abstractmethod
    def clear(self, provider: str) -> None:
        """Supprime les credentials pour le provider donné."""
