from typing import Optional

from backend.core.exceptions import AuthError
from backend.ports.emailProvider import EmailProvider
from backend.core.models.email import Email, EmailListQuery, EmailPage
from backend.adapters.authProvider.GMAIL.gmailTokenStorage import get_gmail_credentials
from backend.adapters.mailProvider.GMAIL.gmailApiService import build_gmail_service
from backend.adapters.mailProvider.GMAIL.gmailMessageParser import parse_gmail_message


class GmailAdapter(EmailProvider):

    def __init__(self):
        gmail_credentials = get_gmail_credentials()
        if not gmail_credentials:
            raise AuthError(
                "credentials Gmail non disponibles. Authentification requise."
            )
        self.gmail_api = build_gmail_service(gmail_credentials)

    def fetch_emails_gmail(
            self,
            max_results: int = 50,
            query: Optional[EmailListQuery] = None,
    ) -> EmailPage:
        q = self._map_core_query_to_gmail(query)
        try:
            # pylint: disable=no-member
            results = (
                self.gmail_api.users()
                .messages()
                .list(
                    userId="me",
                    maxResults=max_results,
                    q=q,
                )
                .execute()
            )

            messages = results.get("messages", [])
            next_page_token = results.get("nextPageToken")

            emails = []
            for msg in messages:
                email_obj = self._get_and_parse_to_email(msg["id"])
                emails.append(email_obj)

            return EmailPage(emails=emails, next_page_token=next_page_token)
        except (OSError, ValueError, KeyError, TypeError) as e:
            raise RuntimeError(
                f"Erreur lors de la récupération des emails: {str(e)}"
            ) from e

    def archive_email_gmail(self, email_id: str) -> bool:
        try:
            # pylint: disable=no-member
            self.gmail_api.users().messages().modify(
                userId="me",
                id=email_id,
                body={"removeLabelIds": ["INBOX"]},
            ).execute()
            return True
        except (OSError, ValueError, KeyError, TypeError):
            return False

    def _get_and_parse_to_email(self, email_id: str) -> Email:
        # pylint: disable=no-member
        message = (
            self.gmail_api.users()
            .messages()
            .get(userId="me", id=email_id, format="full")
            .execute()
        )
        return parse_gmail_message(message)

    def _map_core_query_to_gmail(self, query: Optional[EmailListQuery]) -> str:
        unread = "is:unread"
        if not query:
            return unread
        parts: list[str] = []
        if query.unread_only:
            parts.append(unread)
        if query.after_date:
            # Gmail : after:YYYY/MM/DD
            parts.append(f"after:{query.after_date:%Y/%m/%d}")
        return " ".join(parts) if parts else unread


def fetch_emails_gmail(
    max_results: int = 50,
    query: Optional[EmailListQuery] = None,
) -> EmailPage:
    return GmailAdapter().fetch_emails_gmail(max_results=max_results, query=query)


def archive_email_gmail(email_id: str) -> bool:
    return GmailAdapter().archive_email_gmail(email_id)
