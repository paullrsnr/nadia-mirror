# pylint: disable=invalid-name
"""Adaptateur Outlook pour Microsoft Graph API."""
from typing import Optional

import httpx

from backend.ports.emailProvider import EmailProvider
from backend.core.models.email import EmailListQuery, EmailPage
from backend.core.models.Auth import OutlookTokens
from backend.core.services.Credentials import get_outlook_credentials
from backend.adapters.MailProvider.Outlook.outlookMessageParser import (
    graph_request_headers,
    parse_outlook_message,
)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
GRAPH_PARAM_FILTER = "$filter"


def _outlook_next_token(next_link: Optional[str]) -> Optional[str]:
    """Extrait le token de pagination depuis @odata.nextLink (skiptoken=...)."""
    if not next_link or "$skiptoken=" not in next_link:
        return None
    return next_link.split("$skiptoken=", 1)[-1]


def _outlook_params_from_query(
    max_results: int, query: Optional[EmailListQuery]
) -> dict[str, int | str]:
    """Traduit la requête canonique en paramètres Microsoft Graph ($filter, $top, etc.)."""
    params: dict[str, int | str] = {
        "$top": min(max_results, 500),
        "$orderby": "receivedDateTime desc",
        "$select": (
            "id,conversationId,subject,from,toRecipients,"
            "body,bodyPreview,receivedDateTime"
        ),
    }
    if not query:
        params[GRAPH_PARAM_FILTER] = "isRead eq false"
        return params
    if query.unread_only:
        params[GRAPH_PARAM_FILTER] = "isRead eq false"
    if query.after_date:
        # Graph : receivedDateTime ge YYYY-MM-DD
        date_str = query.after_date.isoformat()
        existing = params.get(GRAPH_PARAM_FILTER, "")
        date_filter = f"receivedDateTime ge {date_str}"
        params[GRAPH_PARAM_FILTER] = f"{existing} and {date_filter}" if existing else date_filter
    return params


class OutlookAdapter(EmailProvider):
    """Adaptateur pour Microsoft Graph (Outlook). Utilise les tokens Outlook."""

    def __init__(self):
        self._tokens: OutlookTokens | None = get_outlook_credentials()
        if not self._tokens or not self._tokens.access_token:
            raise ValueError(
                "Credentials Outlook non disponibles. Authentification requise."
            )

    def _ensure_token(self) -> str:
        """Retourne un access_token valide (recharge si nécessaire)."""
        tokens = get_outlook_credentials()
        if not tokens:
            raise ValueError("Credentials Outlook non disponibles.")
        return tokens.access_token

    def get_emails(
        self,
        max_results: int = 50,
        query: Optional[EmailListQuery] = None,
    ) -> EmailPage:
        """Récupère une page d'emails depuis Outlook (requête canonique → $filter Graph)."""
        access_token = self._ensure_token()
        url = f"{GRAPH_BASE}/me/messages"
        params = _outlook_params_from_query(max_results, query)

        with httpx.Client() as client:
            response = client.get(
                url,
                headers=graph_request_headers(access_token),
                params=params,
            )
            response.raise_for_status()
        data = response.json()
        messages = data.get("value", [])
        next_token = _outlook_next_token(data.get("@odata.nextLink"))

        emails = [parse_outlook_message(msg) for msg in messages]
        return EmailPage(emails=emails, next_page_token=next_token)

    def archive_email(self, email_id: str) -> bool:
        """Archive un email (déplacement vers le dossier Archive)."""
        access_token = self._ensure_token()
        url = f"{GRAPH_BASE}/me/messages/{email_id}/move"
        body = {"destinationId": "archive"}
        try:
            with httpx.Client() as client:
                response = client.post(
                    url,
                    headers=graph_request_headers(access_token),
                    json=body,
                )
                response.raise_for_status()
            return True
        except (httpx.HTTPError, ValueError, KeyError):
            return False
