# pylint: disable=invalid-name
"""Interface abstraite pour les fournisseurs d'email."""
from abc import ABC, abstractmethod
from typing import Optional

from backend.core.models.email import EmailListQuery, EmailPage


class EmailProvider(ABC):
    """Interface pour les fournisseurs d'email.

    La requête est canonique (EmailListQuery) : chaque adapter la traduit
    en format natif (Gmail, Outlook, etc.). Pas de dialecte Gmail en entrée.
    """

    @abstractmethod
    def get_emails(
        self,
        max_results: int = 50,
        query: Optional[EmailListQuery] = None,
    ) -> EmailPage:
        """Récupère une page d'emails. query : requête canonique (unread_only, after_date)."""

    @abstractmethod
    def archive_email(self, email_id: str) -> bool:
        """Archive un email."""
