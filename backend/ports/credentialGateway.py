from abc import ABC, abstractmethod
from typing import Any


class CredentialGateway(ABC):

    @abstractmethod
    def load(self, provider: str) -> Any | None:
        """Charge les credentials pour le provider donné."""

    @abstractmethod
    def save(self, provider: str, credentials: Any) -> None:
        """Sauvegarde les credentials pour le provider donné."""

    @abstractmethod
    def clear(self, provider: str) -> None:
        """Supprime les credentials pour le provider donné."""
