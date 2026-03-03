# pylint: disable=invalid-name
"""Adapter OAuth Outlook : URL d'auth, échange de code, récupération de l'email utilisateur."""
import time
from typing import Optional
from urllib.parse import urlencode

import httpx

from backend.config.settings import auth_settings
from backend.adapters.AuthProvider.Outlook.outlookTokens import OutlookTokens
from backend.ports.oauthPort import OAuthPort


MICROSOFT_GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
_GRAPH_ME = f"{MICROSOFT_GRAPH_BASE_URL}/me"


def _oauth_base_url() -> str:
    return f"https://login.microsoftonline.com/{auth_settings.OUTLOOK_TENANT}/oauth2/v2.0"


def generate_outlook_auth_url(state: str) -> str:
    """Génère l'URL d'authentification OAuth2 Outlook (Microsoft).

    Raises:
        ValueError: Si OUTLOOK_CLIENT_ID n'est pas configuré.
    """
    if not auth_settings.OUTLOOK_CLIENT_ID:
        raise ValueError("OUTLOOK_CLIENT_ID doit être configuré")

    redirect_uri = auth_settings.OUTLOOK_REDIRECT_URI.strip()
    params = {
        "client_id": auth_settings.OUTLOOK_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": " ".join(auth_settings.OUTLOOK_SCOPES),
        "state": state,
        "response_mode": "query",
    }
    return f"{_oauth_base_url()}/authorize?{urlencode(params)}"


def exchange_outlook_code_for_tokens(code: str) -> OutlookTokens:
    """Échange un code OAuth contre des tokens Outlook (access + refresh).

    Raises:
        httpx.HTTPError: En cas d'erreur HTTP.
    """
    data = {
        "client_id": auth_settings.OUTLOOK_CLIENT_ID,
        "client_secret": auth_settings.OUTLOOK_CLIENT_SECRET,
        "code": code,
        "redirect_uri": auth_settings.OUTLOOK_REDIRECT_URI.strip(),
        "grant_type": "authorization_code",
    }

    with httpx.Client() as client:
        response = client.post(f"{_oauth_base_url()}/token", data=data)
        response.raise_for_status()

    body = response.json()
    expires_in = int(body.get("expires_in", 3600))

    return OutlookTokens(
        access_token=body["access_token"],
        refresh_token=body.get("refresh_token", ""),
        expires_at=time.time() + expires_in,
    )


def get_outlook_user_email(tokens: OutlookTokens) -> Optional[str]:
    """Récupère l'email de l'utilisateur via Microsoft Graph /me."""
    try:
        with httpx.Client() as client:
            response = client.get(
                _GRAPH_ME,
                headers={"Authorization": f"Bearer {tokens.access_token}"},
            )
            response.raise_for_status()

        data = response.json()
        return data.get("mail") or data.get("userPrincipalName")
    except Exception:
        return None


class OutlookOAuthPort(OAuthPort):
    """Implémentation du port OAuth pour Outlook."""

    def generate_auth_url(self, state: str) -> str:
        return generate_outlook_auth_url(state)

    def exchange_code(self, code: str) -> OutlookTokens:
        return exchange_outlook_code_for_tokens(code)

    def get_user_email(self, credentials: OutlookTokens) -> Optional[str]:
        return get_outlook_user_email(credentials)
