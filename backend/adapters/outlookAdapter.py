# pylint: disable=invalid-name
"""Adaptateur Outlook pour Microsoft Graph API."""
from datetime import datetime
from typing import Optional, cast

import httpx

from backend.ports.emailProvider import EmailProvider
from backend.core.models.email import (
    Email,
    EmailAddress,
    EmailPage,
)
from backend.core.services.credentialsService import get_outlook_credentials

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
_BODY_FALLBACK = "[Corps non disponible]"


def _headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}


def _parse_address(addr: dict[str, object] | None) -> EmailAddress:
    """Construit EmailAddress depuis un emailAddress Graph."""
    if not isinstance(addr, dict):
        return EmailAddress(email="")
    raw = addr.get("emailAddress") or {}
    email_addr = cast(dict[str, object], raw)
    addr_str = email_addr.get("address")
    name_val = email_addr.get("name")
    return EmailAddress(
        email=str(addr_str) if addr_str else "",
        name=name_val if isinstance(name_val, str) else None,
    )


def _parse_graph_datetime(received: str | None) -> datetime:
    """Parse receivedDateTime Graph en datetime."""
    if not received:
        return datetime.now()
    try:
        return datetime.fromisoformat(str(received).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return datetime.now()


def _body_text_and_html(message: dict[str, object]) -> tuple[str, Optional[str]]:
    """Extrait body_text et body_html depuis le body Graph."""
    body = cast(dict[str, object], message.get("body") or {})
    content = str(body.get("content") or "")
    content_type = str(body.get("contentType") or "text").lower()
    body_preview = str(message.get("bodyPreview") or "")
    if content_type == "text":
        return (content or body_preview or _BODY_FALLBACK, None)
    if content_type == "html":
        return (body_preview or _BODY_FALLBACK, content or None)
    return (body_preview or _BODY_FALLBACK, None)


def _message_to_email(message: dict[str, object]) -> Email:
    """Mappe un message Microsoft Graph vers le modèle Email."""
    msg_id = str(message.get("id") or "")
    body_text, body_html = _body_text_and_html(message)

    from_addr = _parse_address(cast(Optional[dict[str, object]], message.get("from")))
    to_recipients = message.get("toRecipients") or []
    to_addresses = [_parse_address(cast(Optional[dict[str, object]], r)) for r in to_recipients]

    thread_id = str(message.get("conversationId") or msg_id)
    subject = str(message.get("subject") or "")
    snippet_val = message.get("bodyPreview")
    snippet = str(snippet_val) if snippet_val is not None else None

    return Email(
        id=msg_id,
        thread_id=thread_id,
        subject=subject,
        from_address=from_addr,
        to_addresses=to_addresses,
        date=_parse_graph_datetime(cast(Optional[str], message.get("receivedDateTime"))),
        body_text=body_text,
        body_html=body_html,
        snippet=snippet,
    )


class OutlookAdapter(EmailProvider):
    """Adaptateur pour Microsoft Graph (Outlook). Utilise les tokens Outlook."""

    def __init__(self):
        self._tokens = get_outlook_credentials()
        if not self._tokens or not self._tokens.get("access_token"):
            raise ValueError(
                "Credentials Outlook non disponibles. Authentification requise."
            )

    def _ensure_token(self) -> str:
        """Retourne un access_token valide (recharge si nécessaire)."""
        tokens = get_outlook_credentials()
        if not tokens:
            raise ValueError("Credentials Outlook non disponibles.")
        return tokens["access_token"]

    def get_emails(
        self,
        max_results: int = 50,
        query: Optional[str] = None,
    ) -> EmailPage:
        """Récupère une page d'emails depuis Outlook (Microsoft Graph)."""
        access_token = self._ensure_token()
        url = f"{GRAPH_BASE}/me/messages"
        params: dict[str, int | str] = {
            "$top": min(max_results, 500),
            "$orderby": "receivedDateTime desc",
            "$select": (
                "id,conversationId,subject,from,toRecipients,"
                "body,bodyPreview,receivedDateTime"
            ),
        }
        if query and query.strip():
            q = query.strip().lower()
            if "unread" in q or "is:unread" in q:
                params["$filter"] = "isRead eq false"

        with httpx.Client() as client:
            response = client.get(
                url,
                headers=_headers(access_token),
                params=params,
            )
            response.raise_for_status()
        data = response.json()
        messages = data.get("value", [])
        next_link = data.get("@odata.nextLink")
        next_token = None
        if next_link and "$skiptoken=" in next_link:
            next_token = next_link.split("$skiptoken=", 1)[-1]

        emails = [_message_to_email(message) for message in messages]
        return EmailPage(emails=emails, next_page_token=next_token)

    def archive_email(self, email_id: str) -> bool:
        """Archive un email (déplacement vers le dossier Archive)."""
        access_token = self._ensure_token()
        url = f"{GRAPH_BASE}/me/messages/{email_id}/move"
        # Dossier bien connu "archive" (Microsoft Graph)
        body = {"destinationId": "archive"}
        try:
            with httpx.Client() as client:
                response = client.post(
                    url,
                    headers=_headers(access_token),
                    json=body,
                )
                response.raise_for_status()
            return True
        except (httpx.HTTPError, ValueError, KeyError):
            return False
