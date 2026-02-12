# pylint: disable=invalid-name
"""Interface abstraite pour les fournisseurs d'email."""
from abc import ABC, abstractmethod
from typing import Optional

from backend.core.models.email import EmailPage


class EmailProvider(ABC):
    """Interface pour les fournisseurs d'email."""

    @abstractmethod
    def get_emails(
        self,
        max_results: int = 50,
        query: Optional[str] = None,
    ) -> EmailPage:
        """Récupère une page d'emails."""

    @abstractmethod
    def archive_email(self, email_id: str) -> bool:
        """Archive un email."""
