# pylint: disable=invalid-name
"""Adaptateur Gmail pour l'API Google."""
from typing import Optional

from backend.core.exceptions import AuthError
from backend.ports.emailProvider import EmailProvider
from backend.core.models.Email import Email, EmailListQuery, EmailPage
from backend.adapters.AuthProvider.GMAIL.gmailTokenStorage import get_gmail_credentials
from backend.adapters.MailProvider.GMAIL.gmailApiService import build_gmail_service
from backend.adapters.MailProvider.GMAIL.gmailMessageParser import parse_gmail_message


_GMAIL_QUERY_UNREAD = "is:unread"


def _gmail_query_string(query: Optional[EmailListQuery]) -> str:
    """Traduit la requête canonique en chaîne de requête Gmail."""
    if not query:
        return _GMAIL_QUERY_UNREAD
    parts: list[str] = []
    if query.unread_only:
        parts.append(_GMAIL_QUERY_UNREAD)
    if query.after_date:
        # Gmail : after:YYYY/MM/DD
        parts.append(f"after:{query.after_date:%Y/%m/%d}")
    return " ".join(parts) if parts else _GMAIL_QUERY_UNREAD


class GmailAdapter(EmailProvider):
    """Adaptateur pour l'API Gmail. Utilise uniquement les credentials Gmail."""

    def __init__(self):
        self.gmail_api = None
        self._ensure_service()

    def _ensure_service(self) -> None:
        """Initialise le client Gmail si les credentials Gmail sont disponibles."""
        gmail_credentials = get_gmail_credentials()
        if gmail_credentials:
            self.gmail_api = build_gmail_service(gmail_credentials)
        else:
            raise AuthError(
                "Credentials Gmail non disponibles. Authentification requise."
            )

    def fetch_emails(
        self,
        max_results: int = 50,
        query: Optional[EmailListQuery] = None,
    ) -> EmailPage:
        """Fetche une page d'emails depuis Gmail (requête canonique → query Gmail)."""
        q = _gmail_query_string(query)
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

    def _get_and_parse_to_email(self, email_id: str) -> Email:
        """Récupère le message Gmail puis le parse en objet métier Email."""
        # pylint: disable=no-member
        message = (
            self.gmail_api.users()
            .messages()
            .get(userId="me", id=email_id, format="full")
            .execute()
        )
        return parse_gmail_message(message)

    def archive_email(self, email_id: str) -> bool:
        """Archive un email (retire le label INBOX)."""
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
