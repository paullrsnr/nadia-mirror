import time
from typing import Optional
from urllib.parse import urlencode

import httpx

from backend.config.settings import auth_settings
from backend.adapters.authProvider.Outlook.outlookTokens import OutlookTokens
from backend.adapters.outlook_graph import GRAPH_BASE


def generate_outlook_auth_url(state: str) -> str:
    if not auth_settings.OUTLOOK_CLIENT_ID:
        raise ValueError("OUTLOOK_CLIENT_ID doit être configuré")
    try:
        params = {
            "client_id": auth_settings.OUTLOOK_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": auth_settings.OUTLOOK_REDIRECT_URI.strip(),
            "scope": " ".join(auth_settings.OUTLOOK_SCOPES),
            "state": state,
            "response_mode": "query",
        }
        return (
            f"https://login.microsoftonline.com/{auth_settings.OUTLOOK_TENANT}"
            f"/oauth2/v2.0/authorize?{urlencode(params)}"
        )
    except Exception as e:
        raise ValueError(f"Erreur génération URL auth Outlook: {e!s}") from e


def get_outlook_tokens(code: str) -> OutlookTokens:
    return _exchange_outlook_code_for_tokens(code)


def refresh_outlook_tokens(refresh_token: str) -> OutlookTokens:
    url = f"https://login.microsoftonline.com/{auth_settings.OUTLOOK_TENANT}/oauth2/v2.0/token"
    data = {
        "client_id": auth_settings.OUTLOOK_CLIENT_ID,
        "client_secret": auth_settings.OUTLOOK_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    response = httpx.post(url, data=data)
    response.raise_for_status()

    body = response.json()
    expires_in = int(body.get("expires_in", 3600))
    return OutlookTokens(
        access_token=body["access_token"],
        refresh_token=body.get("refresh_token") or refresh_token,
        expires_at_timestamp=time.time() + expires_in,
    )


def get_outlook_user_email(tokens: OutlookTokens) -> Optional[str]:
    try:
        response = httpx.Client().get(
            f"{GRAPH_BASE}/me",
            headers={"Authorization": f"Bearer {tokens.access_token}"},
        )
        response.raise_for_status()

        data = response.json()
        return data.get("mail") or data.get("userPrincipalName")
    except Exception:
        return None


def _exchange_outlook_code_for_tokens(code: str) -> OutlookTokens:
    data = {
        "client_id": auth_settings.OUTLOOK_CLIENT_ID,
        "client_secret": auth_settings.OUTLOOK_CLIENT_SECRET,
        "code": code,
        "redirect_uri": auth_settings.OUTLOOK_REDIRECT_URI.strip(),
        "grant_type": "authorization_code",
    }

    response = httpx.post(
        f"https://login.microsoftonline.com/{auth_settings.OUTLOOK_TENANT}/oauth2/v2.0/token",
        data=data,
    )
    response.raise_for_status()

    body = response.json()
    expires_in = int(body.get("expires_in", 3600))

    return OutlookTokens(
        access_token=body["access_token"],
        refresh_token=body.get("refresh_token", ""),
        expires_at_timestamp=time.time() + expires_in,
    )
