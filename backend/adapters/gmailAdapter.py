# pylint: disable=invalid-name
"""Adaptateur Gmail pour l'API Google."""
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List, Optional, Tuple

from googleapiclient.discovery import build

from backend.ports.emailProvider import EmailProvider
from backend.api.schemas import Email, EmailAttachment
from backend.api.routers.auth_router import get_credentials
from backend.utils.emailParser import parse_email_address, extract_email_body


class GmailAdapter(EmailProvider):
    """Adaptateur pour l'API Gmail."""

    def __init__(self):
        self.service = None
        self._ensure_service()

    def _ensure_service(self):
        """Initialise le service Gmail si les credentials sont disponibles."""
        credentials = get_credentials()
        if credentials:
            # pylint: disable=no-member
            self.service = build("gmail", "v1", credentials=credentials)
        else:
            raise ValueError(
                "Credentials Gmail non disponibles. Authentification requise."
            )

    def get_emails(
        self,
        max_results: int = 50,
        query: Optional[str] = None,
        page_token: Optional[str] = None,
    ) -> Tuple[List[Email], Optional[str]]:
        """Récupère une liste d'emails depuis Gmail."""
        if not self.service:
            self._ensure_service()

        try:
            # pylint: disable=no-member
            results = (
                self.service.users()
                .messages()
                .list(
                    userId="me",
                    maxResults=max_results,
                    q=query,
                    pageToken=page_token,
                )
                .execute()
            )

            messages = results.get("messages", [])
            next_page_token = results.get("nextPageToken")

            emails = []
            for msg in messages:
                email_obj = self._get_email_details(msg["id"])
                emails.append(email_obj)

            return emails, next_page_token
        except Exception as e:
            raise RuntimeError(
                f"Erreur lors de la récupération des emails: {str(e)}"
            ) from e

    def _get_email_details(self, email_id: str) -> Email:
        """Récupère les détails d'un email depuis Gmail."""
        # pylint: disable=no-member
        message = (
            self.service.users()
            .messages()
            .get(userId="me", id=email_id, format="full")
            .execute()
        )
        return self._parse_gmail_message(message)

    def _parse_gmail_message(self, message: dict) -> Email:
        """Parse un message Gmail en objet Email."""
        payload = message["payload"]
        headers = payload.get("headers", [])

        # Extraire les headers
        header_dict = {h["name"].lower(): h["value"] for h in headers}

        # Parser les adresses
        from_addr = parse_email_address(header_dict.get("from", ""))
        to_addrs = [
            parse_email_address(addr)
            for addr in header_dict.get("to", "").split(",")
            if addr.strip()
        ]
        cc_addrs = (
            [
                parse_email_address(addr)
                for addr in header_dict.get("cc", "").split(",")
                if addr.strip()
            ]
            if header_dict.get("cc")
            else []
        )

        # Parser la date (format RFC 2822)
        date_str = header_dict.get("date", "")
        try:
            date = parsedate_to_datetime(date_str) if date_str else datetime.now()
        except (ValueError, TypeError):
            date = datetime.now()

        # Extraire le corps de l'email
        body_text, body_html = extract_email_body(payload)

        # Extraire les pièces jointes
        attachments = []
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("filename") and part.get("body", {}).get("attachmentId"):
                    attachments.append(
                        EmailAttachment(
                            filename=part["filename"],
                            mime_type=part.get("mimeType", "application/octet-stream"),
                            size=part.get("body", {}).get("size", 0),
                            attachment_id=part["body"]["attachmentId"],
                        )
                    )

        return Email(
            id=message["id"],
            thread_id=message["threadId"],
            subject=header_dict.get("subject", ""),
            from_address=from_addr,
            to_addresses=to_addrs,
            cc_addresses=cc_addrs,
            bcc_addresses=[],
            date=date,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
            labels=message.get("labelIds", []),
            snippet=message.get("snippet"),
        )

    # get_email - À implémenter
    # get_thread - À implémenter
    # get_threads - À implémenter
    # send_email - À implémenter

    def archive_email(self, email_id: str) -> bool:
        """Archive un email (supprime le label INBOX)."""
        if not self.service:
            self._ensure_service()

        try:
            # pylint: disable=no-member
            self.service.users().messages().modify(
                userId="me",
                id=email_id,
                body={"removeLabelIds": ["INBOX"]},
            ).execute()
            return True
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'archivage: {str(e)}") from e

    # mark_as_read - À implémenter
