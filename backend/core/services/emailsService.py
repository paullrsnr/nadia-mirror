# pylint: disable=invalid-name
"""Use case : liste d'emails et archivage (délègue au port EmailProvider)."""
from typing import Optional

from backend.core.models.email import EmailListResult
from backend.ports.emailProvider import EmailProvider


class EmailsService:
    """Service métier : récupération et archivage d'emails (use case)."""

    def __init__(self, email_provider: EmailProvider):
        self._provider = email_provider

    def get_emails(
        self,
        max_results: int = 50,
        query: Optional[str] = None,
        page_token: Optional[str] = None,
        page: int = 1,
    ) -> EmailListResult:
        """Récupère une liste paginée d'emails."""
        emails, _ = self._provider.get_emails(
            max_results=max_results,
            query=query,
            page_token=page_token,
        )
        return EmailListResult(
            emails=emails,
            total=len(emails),
            page=page,
            page_size=max_results,
        )

    def archive_email(self, email_id: str) -> bool:
        """Archive un email."""
        return self._provider.archive_email(email_id)
