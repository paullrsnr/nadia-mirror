from abc import ABC, abstractmethod
from typing import Optional

from backend.core.models.email import EmailListQuery, EmailPage


class EmailProviderGateway(ABC):
    @abstractmethod
    def fetch_emails(
        self,
        provider: str,
        max_results: int = 50,
        query: Optional[EmailListQuery] = None,
    ) -> EmailPage:
        """Récupère une page d'emails pour le provider donné."""

    @abstractmethod
    def archive_email(self, provider: str, email_id: str) -> bool:
        """Archive un email pour le provider donné."""
