"""Interface abstraite pour un flux OAuth (génération URL, échange de code, identité)."""
from abc import ABC, abstractmethod
from typing import Any


class OAuthPort(ABC):
    """Contrat pour un provider OAuth : URL → code → credentials → identité."""

    @abstractmethod
    def generate_auth_url(self, state: str) -> str:
        """Génère l'URL d'autorisation OAuth à ouvrir par l'utilisateur."""

    @abstractmethod
    def exchange_code(self, code: str) -> Any:
        """Échange le code de callback contre des credentials/tokens."""

    @abstractmethod
    def get_user_email(self, credentials: Any) -> str | None:
        """Récupère l'adresse email de l'utilisateur à partir des credentials."""
