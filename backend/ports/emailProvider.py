from abc import ABC, abstractmethod
from typing import Optional

from backend.core.models.email import EmailListQuery, EmailPage


class EmailProvider(ABC):
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
