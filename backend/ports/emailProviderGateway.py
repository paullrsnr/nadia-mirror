from abc import ABC, abstractmethod
from typing import Optional

from backend.core.models.email import AttachmentContent, EmailListQuery, EmailPage, DraftEmail


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

    @abstractmethod
    def get_attachment_content(self, provider: str, email_id: str, attachment_id: str) -> bytes:
        """Récupère le contenu binaire d'une pièce jointe pour le provider donné."""

    @abstractmethod
    def mark_as_read(self, provider: str, email_id: str) -> bool:
        """Marque un email comme lu pour le provider donné."""

    @abstractmethod
    def send_email(self, provider: str, draft: DraftEmail, attachments: list[AttachmentContent]) -> bool:
        """Envoie un email pour le provider donné."""
