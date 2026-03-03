# pylint: disable=invalid-name
"""Interface abstraite pour les fournisseurs d'email."""
from abc import ABC, abstractmethod
from typing import Optional

from backend.core.models.Email import EmailListQuery, EmailPage


class EmailProvider(ABC):
    """Interface pour les fournisseurs d'email.

    La requête est canonique (EmailListQuery) : chaque adapter la traduit
    en format natif (Gmail, Outlook, etc.). Pas de dialecte Gmail en entrée.
    """

    @abstractmethod
    def fetch_emails(
        self,
        max_results: int = 50,
        query: Optional[EmailListQuery] = None,
    ) -> EmailPage:
        """Fetche une page d'emails depuis le provider distant. query : requête canonique."""

    @abstractmethod
    def archive_email(self, email_id: str) -> bool:
        """Archive un email."""
