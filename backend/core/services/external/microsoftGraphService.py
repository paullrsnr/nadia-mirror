# pylint: disable=invalid-name
"""Service pour les appels à l'API Microsoft Graph."""
import time
from typing import Optional
from urllib.parse import urlencode

import httpx

from backend.config.settings import auth_settings
from backend.core.models.Auth import OutlookTokens


# URLs Microsoft Graph et OAuth
MICROSOFT_GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
MICROSOFT_GRAPH_ME_ENDPOINT = f"{MICROSOFT_GRAPH_BASE_URL}/me"


def _get_microsoft_oauth_base_url() -> str:
    """Retourne l'URL de base pour OAuth Microsoft selon le tenant."""
    tenant = auth_settings.OUTLOOK_TENANT
    return f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0"


def generate_outlook_auth_url(state: str) -> str:
    """Génère une URL d'authentification OAuth2 pour Outlook (Microsoft).
    
    Args:
        state: État à inclure dans l'URL (généralement le nom du provider)
        
    Returns:
        str: URL d'authentification complète
        
    Raises:
        ValueError: Si OUTLOOK_CLIENT_ID n'est pas configuré
    """
    if not auth_settings.OUTLOOK_CLIENT_ID:
        raise ValueError("OUTLOOK_CLIENT_ID doit être configuré")
    
    redirect_uri = auth_settings.OUTLOOK_REDIRECT_URI.strip()
    base = f"{_get_microsoft_oauth_base_url()}/authorize"
    scopes = " ".join(auth_settings.OUTLOOK_SCOPES)
    
    params = {
        "client_id": auth_settings.OUTLOOK_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scopes,
        "state": state,
        "response_mode": "query",
    }
    return f"{base}?{urlencode(params)}"


def exchange_outlook_code_for_tokens(code: str) -> OutlookTokens:
    """Échange un code OAuth contre des tokens Outlook.
    
    Args:
        code: Code OAuth retourné par Microsoft
        
    Returns:
        OutlookTokens: Tokens Microsoft (access_token, refresh_token, expires_at)
        
    Raises:
        httpx.HTTPError: En cas d'erreur HTTP
    """
    redirect_uri = auth_settings.OUTLOOK_REDIRECT_URI.strip()
    url = f"{_get_microsoft_oauth_base_url()}/token"
    
    data = {
        "client_id": auth_settings.OUTLOOK_CLIENT_ID,
        "client_secret": auth_settings.OUTLOOK_CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    
    with httpx.Client() as client:
        response = client.post(url, data=data)
        response.raise_for_status()
    
    body = response.json()
    expires_in = int(body.get("expires_in", 3600))
    
    return OutlookTokens(
        access_token=body["access_token"],
        refresh_token=body.get("refresh_token", ""),
        expires_at=time.time() + expires_in,
    )


def get_user_email_address(tokens: OutlookTokens) -> Optional[str]:
    """Récupère l'adresse email de l'utilisateur via Microsoft Graph.
    
    Args:
        tokens: Tokens Microsoft OAuth2
        
    Returns:
        Optional[str]: Adresse email ou None en cas d'erreur
    """
    try:
        with httpx.Client() as client:
            response = client.get(
                MICROSOFT_GRAPH_ME_ENDPOINT,
                headers={"Authorization": f"Bearer {tokens.access_token}"},
            )
            response.raise_for_status()
        
        data = response.json()
        return data.get("mail") or data.get("userPrincipalName")
    except Exception:
        return None
