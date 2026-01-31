# pylint: disable=invalid-name
"""Interface abstraite pour les fournisseurs d'email."""
from abc import ABC, abstractmethod
from typing import List, Optional

from backend.core.models.email import Email


class EmailProvider(ABC):
    """Interface pour les fournisseurs d'email."""

    @abstractmethod
    def get_emails(
        self,
        max_results: int = 50,
        query: Optional[str] = None,
        page_token: Optional[str] = None,
    ) -> tuple[List[Email], Optional[str]]:
        """Récupère une liste d'emails."""

    # get_email - À implémenter
    # get_thread - À implémenter
    # get_threads - À implémenter
    # send_email - À implémenter

    @abstractmethod
    def archive_email(self, email_id: str) -> bool:
        """Archive un email."""

    # mark_as_read - À implémenter
