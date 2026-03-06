from typing import Optional

import httpx

from backend.core.exceptions import AuthError
from backend.ports.emailProvider import EmailProvider
from backend.core.models.Email import EmailListQuery, EmailPage
from backend.adapters.authProvider.Outlook.outlookTokens import OutlookTokens
from backend.adapters.authProvider.Outlook.outlookTokenStorage import get_outlook_credentials
from backend.adapters.mailProvider.Outlook.outlookMessageParser import (
    graph_request_headers,
    parse_outlook_message,
)
from backend.adapters.outlook_graph import GRAPH_BASE, GRAPH_PARAM_FILTER


class OutlookAdapter(EmailProvider):

    def __init__(self):
        tokens = get_outlook_credentials()
        if not tokens or not tokens.access_token:
            raise AuthError(
                "Credentials Outlook non disponibles. Authentification requise."
            )
        self._tokens: OutlookTokens = tokens

    def _access_token(self) -> str:
        tokens = get_outlook_credentials()
        if not tokens:
            raise AuthError("Credentials Outlook non disponibles.")
        return tokens.access_token

    def _build_params(self, max_results: int, query: Optional[EmailListQuery]) -> dict[str, int | str]:
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
            existing = params.get(GRAPH_PARAM_FILTER, "")
            date_filter = f"receivedDateTime ge {query.after_date.isoformat()}"
            params[GRAPH_PARAM_FILTER] = f"{existing} and {date_filter}" if existing else date_filter
        return params

    def _next_token(self, next_link: Optional[str]) -> Optional[str]:
        if not next_link or "$skiptoken=" not in next_link:
            return None
        return next_link.split("$skiptoken=", 1)[-1]

    def fetch_emails(
        self,
        max_results: int = 50,
        query: Optional[EmailListQuery] = None,
    ) -> EmailPage:
        access_token = self._access_token()
        params = self._build_params(max_results, query)

        with httpx.Client() as client:
            response = client.get(
                f"{GRAPH_BASE}/me/messages",
                headers=graph_request_headers(access_token),
                params=params,
            )
            response.raise_for_status()
            data = response.json()
        emails = [parse_outlook_message(msg) for msg in data.get("value", [])]
        return EmailPage(emails=emails, next_page_token=self._next_token(data.get("@odata.nextLink")))

    def archive_email(self, email_id: str) -> bool:
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
