from typing import Optional

from backend.core.exceptions import ProviderError
from backend.core.models.email import AttachmentContent, Provider, EmailListQuery, EmailPage, DraftEmail
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
            return GmailAdapter().fetch_emails_gmail(max_results=max_results, query=query)
        if provider == Provider.OUTLOOK.value:
            return OutlookAdapter().fetch_emails_outlook(max_results=max_results, query=query)
        raise ProviderError(f"Provider inconnu : {provider!r}")

    def archive_email(self, provider: str, email_id: str) -> bool:
        if provider == Provider.GMAIL.value:
            return GmailAdapter().archive_email_gmail(email_id)
        if provider == Provider.OUTLOOK.value:
            return OutlookAdapter().archive_email_outlook(email_id)
        raise ProviderError(f"Provider inconnu : {provider!r}")

    def get_attachment_content(self, provider: str, email_id: str, attachment_id: str) -> bytes:
        if provider == Provider.GMAIL.value:
            return GmailAdapter().get_attachment_gmail(email_id, attachment_id)
        if provider == Provider.OUTLOOK.value:
            return OutlookAdapter().get_attachment_outlook(email_id, attachment_id)
        raise ProviderError(f"Provider inconnu : {provider!r}")

    def mark_as_read(self, provider: str, email_id: str) -> bool:
        if provider == Provider.GMAIL.value:
            return GmailAdapter().mark_as_read_gmail(email_id)
        if provider == Provider.OUTLOOK.value:
            return OutlookAdapter().mark_as_read_outlook(email_id)
        raise ProviderError(f"Provider inconnu : {provider!r}")

    def send_email(self, provider: str, draft: DraftEmail, attachments: list[AttachmentContent]) -> bool:
        if provider == Provider.GMAIL.value:
            return GmailAdapter().send_email_gmail(draft, attachments)
        if provider == Provider.OUTLOOK.value:
            return OutlookAdapter().send_email_outlook(draft, attachments)
        raise ProviderError(f"Provider inconnu : {provider!r}")
