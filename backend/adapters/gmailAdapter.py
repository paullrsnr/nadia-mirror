# pylint: disable=invalid-name
"""Adaptateur Gmail pour l'API Google."""
from typing import Optional

from googleapiclient.discovery import build

from backend.ports.emailProvider import EmailProvider
from backend.core.models.email import Email, EmailPage
from backend.core.services.credentialsService import get_gmail_credentials
from backend.adapters.gmailMessageParser import parse_gmail_message


class GmailAdapter(EmailProvider):
    """Adaptateur pour l'API Gmail. Utilise uniquement les credentials Gmail."""

    def __init__(self):
        self.gmail_api = None
        self._ensure_service()

    def _ensure_service(self) -> None:
        """Initialise le client Gmail si les credentials Gmail sont disponibles."""
        gmail_credentials = get_gmail_credentials()
        if gmail_credentials:
            # pylint: disable=no-member
            self.gmail_api = build("gmail", "v1", credentials=gmail_credentials)
        else:
            raise ValueError(
                "Credentials Gmail non disponibles. Authentification requise."
            )

    # Query Gmail par défaut : non lus uniquement (évite de charger toute la boîte)
    _DEFAULT_QUERY_UNREAD = "is:unread"

    def get_emails(
        self,
        max_results: int = 50,
        query: Optional[str] = None,
    ) -> EmailPage:
        """Récupère une page d'emails depuis Gmail (non lus par défaut)."""
        q = (query or "").strip() or self._DEFAULT_QUERY_UNREAD
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
