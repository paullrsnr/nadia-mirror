from typing import Optional

from backend.core.exceptions import ProviderError
from backend.core.models.email import Provider, EmailListQuery, EmailPage
from backend.ports.emailProviderGateway import EmailProviderGateway
from backend.adapters.mailProvider.GMAIL.gmailAdapter import fetch_emails_gmail, archive_email_gmail
from backend.adapters.mailProvider.Outlook.outlookAdapter import fetch_emails_outlook, archive_email_outlook


class EmailProviderGatewayAdapter(EmailProviderGateway):
    def fetch_emails(
        self,
        provider: str,
        max_results: int = 50,
        query: Optional[EmailListQuery] = None,
    ) -> EmailPage:
        if provider == Provider.GMAIL.value:
            return fetch_emails_gmail(max_results=max_results, query=query)
        if provider == Provider.OUTLOOK.value:
            return fetch_emails_outlook(max_results=max_results, query=query)
        raise ProviderError(f"Provider inconnu : {provider!r}")

    def archive_email(self, provider: str, email_id: str) -> bool:
        if provider == Provider.GMAIL.value:
            return archive_email_gmail(email_id)
        if provider == Provider.OUTLOOK.value:
            return archive_email_outlook(email_id)
        raise ProviderError(f"Provider inconnu : {provider!r}")
