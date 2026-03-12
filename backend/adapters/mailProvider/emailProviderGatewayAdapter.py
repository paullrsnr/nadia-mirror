from typing import Optional

from backend.core.exceptions import ProviderError
from backend.core.models.email import Provider, EmailListQuery, EmailPage
from backend.ports.emailProviderGateway import EmailProviderGateway
from backend.adapters.mailProvider.GMAIL.gmailAdapter import GmailAdapter
from backend.adapters.mailProvider.Outlook.outlookAdapter import OutlookAdapter


class EmailProviderGatewayAdapter(EmailProviderGateway):
    def fetch_emails(
        self,
        provider: str,
        max_results: int = 50,
        query: Optional[EmailListQuery] = None,
    ) -> EmailPage:
        if provider == Provider.GMAIL.value:
            return GmailAdapter().fetch_emails(max_results=max_results, query=query)
        if provider == Provider.OUTLOOK.value:
            return OutlookAdapter().fetch_emails(max_results=max_results, query=query)
        raise ProviderError(f"Provider inconnu : {provider!r}")

    def archive_email(self, provider: str, email_id: str) -> bool:
        if provider == Provider.GMAIL.value:
            return GmailAdapter().archive_email(email_id)
        if provider == Provider.OUTLOOK.value:
            return OutlookAdapter().archive_email(email_id)
        raise ProviderError(f"Provider inconnu : {provider!r}")
