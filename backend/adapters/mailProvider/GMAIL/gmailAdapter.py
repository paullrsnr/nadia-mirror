import base64
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from backend.core.exceptions import AuthError
from backend.core.models.email import AttachmentContent, Email, EmailListQuery, EmailPage, DraftEmail
from backend.adapters.authProvider.GMAIL.gmailTokenStorage import (
    get_gmail_credentials,
    clear_gmail_credentials,
)
from backend.adapters.mailProvider.GMAIL.gmailApiService import build_gmail_service
from backend.adapters.mailProvider.GMAIL.gmailMessageParser import parse_gmail_message


class GmailAdapter:

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
        except Exception as e:
            # Cas classique quand Google invalide le refresh token : invalid_grant.
            # On purge le token local pour forcer une reconnexion propre.
            error_message = str(e)
            if "invalid_grant" in error_message:
                clear_gmail_credentials()
                raise AuthError(
                    "Session Gmail expirée ou invalide. Reconnexion requise."
                ) from e
            raise RuntimeError(
                f"Erreur lors de la récupération des emails: {error_message}"
            ) from e

    def get_attachment_gmail(self, email_id: str, attachment_id: str) -> bytes:
        # pylint: disable=no-member
        result = (
            self.gmail_api.users()
            .messages()
            .attachments()
            .get(userId="me", messageId=email_id, id=attachment_id)
            .execute()
        )
        data = result.get("data", "")
        padded = data + "=" * (-len(data) % 4)
        return base64.urlsafe_b64decode(padded)

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

    def send_email_gmail(self, draft: DraftEmail, attachments: list[AttachmentContent]) -> bool:
        try:
            if draft.body_html:
                body_part = MIMEMultipart("alternative")
                body_part.attach(MIMEText(draft.body_text, "plain"))
                body_part.attach(MIMEText(draft.body_html, "html"))
            else:
                body_part = MIMEText(draft.body_text)

            if attachments:
                message = MIMEMultipart("mixed")
                message.attach(body_part)
                for attachment in attachments:
                    maintype, _, subtype = attachment.mime_type.partition("/")
                    part = MIMEBase(maintype or "application", subtype or "octet-stream")
                    part.set_payload(attachment.content)
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition", f'attachment; filename="{attachment.filename}"'
                    )
                    message.attach(part)
            else:
                message = body_part
            message["To"] = ", ".join(a.email for a in draft.to_addresses)
            message["Subject"] = draft.subject
            if draft.cc_addresses:
                message["Cc"] = ", ".join(a.email for a in draft.cc_addresses)
            if draft.bcc_addresses:
                message["Bcc"] = ", ".join(a.email for a in draft.bcc_addresses)
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            # pylint: disable=no-member
            self.gmail_api.users().messages().send(
                userId="me",
                body={"raw": raw},
            ).execute()
            return True
        except (OSError, ValueError, KeyError, TypeError):
            return False

    def mark_as_read_gmail(self, email_id: str) -> bool:
        try:
            # pylint: disable=no-member
            self.gmail_api.users().messages().modify(
                userId="me",
                id=email_id,
                body={"removeLabelIds": ["UNREAD"]},
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
        if not query:
            return "in:inbox is:unread"
        parts: list[str] = []
        if query.sent_only:
            parts.append("in:sent")
        else:
            parts.append("in:inbox")
            if query.unread_only:
                parts.append("is:unread")
        if query.after_date:
            parts.append(f"after:{query.after_date:%Y/%m/%d}")
        return " ".join(parts)
