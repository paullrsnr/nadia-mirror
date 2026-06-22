import base64
from typing import Optional

import httpx

from backend.core.exceptions import AuthError
from backend.core.models.email import EmailListQuery, EmailPage
from backend.adapters.authProvider.Outlook.outlookTokens import OutlookTokens
from backend.adapters.authProvider.Outlook.outlookTokenStorage import load_outlook_credentials
from backend.adapters.mailProvider.Outlook.outlookMessageParser import (
    graph_request_headers,
    parse_outlook_message,
)
from backend.adapters.outlook_graph import GRAPH_BASE


class OutlookAdapter:


    def __init__(self):
        tokens = load_outlook_credentials()
        if not tokens or not tokens.access_token:
            raise AuthError(
                "credentials Outlook non disponibles. Authentification requise."
            )
        self._tokens: OutlookTokens = tokens


    def fetch_emails_outlook(
        self,
        max_results: int = 50,
        query: Optional[EmailListQuery] = None,
    ) -> EmailPage:
        access_token = self._access_token()
        params = self._build_params(max_results, query)
        folder = "SentItems" if (query and query.sent_only) else "inbox"

        with httpx.Client() as client:
            response = client.get(
                f"{GRAPH_BASE}/me/mailFolders/{folder}/messages",
                headers=graph_request_headers(access_token),
                params=params,
            )
            response.raise_for_status()
            data = response.json()
        emails = [parse_outlook_message(msg) for msg in data.get("value", [])]
        return EmailPage(emails=emails, next_page_token=self._next_token(data.get("@odata.nextLink")))

    def get_attachment_outlook(self, email_id: str, attachment_id: str) -> bytes:
        access_token = self._access_token()
        url = f"{GRAPH_BASE}/me/messages/{email_id}/attachments/{attachment_id}"
        with httpx.Client() as client:
            response = client.get(url, headers=graph_request_headers(access_token))
            response.raise_for_status()
            data = response.json()
        return base64.b64decode(data.get("contentBytes", ""))

    def archive_email_outlook(self, email_id: str) -> bool:
        access_token = self._access_token()
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

    def mark_as_read_outlook(self, email_id: str) -> bool:
        access_token = self._access_token()
        url = f"{GRAPH_BASE}/me/messages/{email_id}"
        body = {"isRead": True}
        try:
            with httpx.Client() as client:
                response = client.patch(
                    url,
                    headers=graph_request_headers(access_token),
                    json=body,
                )
                response.raise_for_status()
            return True
        except (httpx.HTTPError, ValueError, KeyError):
            return False

    def _access_token(self) -> str:
        tokens = load_outlook_credentials()
        if not tokens:
            raise AuthError("credentials Outlook non disponibles.")
        return tokens.access_token

    def _build_params(self, max_results: int, query: Optional[EmailListQuery]) -> dict[str, int | str]:
        GRAPH_PARAM_FILTER = "$filter"
        params: dict[str, int | str] = {
            "$top": min(max_results, 500),
            "$orderby": "receivedDateTime desc",
            "$select": (
                "id,conversationId,subject,from,toRecipients,"
                "body,bodyPreview,receivedDateTime,hasAttachments"
            ),
            "$expand": "attachments($select=id,name,contentType,size)",
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


def fetch_emails_outlook(max_results: int = 50, query: Optional[EmailListQuery] = None) -> EmailPage:
    return OutlookAdapter().fetch_emails_outlook(max_results=max_results, query=query)


def archive_email_outlook(email_id: str) -> bool:
    return OutlookAdapter().archive_email_outlook(email_id)


def get_attachment_outlook(email_id: str, attachment_id: str) -> bytes:
    return OutlookAdapter().get_attachment_outlook(email_id, attachment_id)


def mark_as_read_outlook(email_id: str) -> bool:
    return OutlookAdapter().mark_as_read_outlook(email_id)