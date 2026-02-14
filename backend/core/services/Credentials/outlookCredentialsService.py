# pylint: disable=invalid-name
"""Gestion des credentials OAuth Outlook (sauvegarde, chargement, suppression, refresh)."""
import json
import logging
import os
import time

import httpx

from backend.config.settings import storage_settings, auth_settings
from backend.config.providers import EmailProvider
from backend.core.models.Auth import OutlookTokens

logger = logging.getLogger(__name__)

PROVIDER_OUTLOOK = EmailProvider.OUTLOOK.value


def _outlook_tokens_path() -> os.PathLike:
    """Chemin du fichier de tokens Outlook."""
    return storage_settings.tokens_file(PROVIDER_OUTLOOK)


def _save_outlook_credentials(tokens: OutlookTokens) -> None:
    """Sauvegarde les tokens Outlook (access_token, refresh_token, expires_at)."""
    path = _outlook_tokens_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tokens.model_dump(), f)
    os.chmod(path, 0o600)


def _refresh_outlook_tokens(refresh_token: str) -> OutlookTokens:
    """Échange le refresh_token Outlook contre de nouveaux tokens (Microsoft token endpoint)."""
    tenant = auth_settings.OUTLOOK_TENANT
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    data = {
        "client_id": auth_settings.OUTLOOK_CLIENT_ID,
        "client_secret": auth_settings.OUTLOOK_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    with httpx.Client() as client:
        response = client.post(url, data=data)
        response.raise_for_status()
    body = response.json()
    expires_in = int(body.get("expires_in", 3600))
    return OutlookTokens(
        access_token=body["access_token"],
        refresh_token=body.get("refresh_token") or refresh_token,
        expires_at=time.time() + expires_in,
    )


def _load_outlook_credentials() -> OutlookTokens | None:
    """Charge les tokens Outlook ; refresh si expirés (marge 5 min)."""
    path = _outlook_tokens_path()
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            tokens_dict = json.load(f)
    except Exception as error:
        logger.exception("Erreur chargement tokens Outlook: %s", error)
        return None
    access_token = tokens_dict.get("access_token")
    refresh_token = tokens_dict.get("refresh_token")
    if not access_token or not refresh_token:
        return None
    expires_at = tokens_dict.get("expires_at", 0)
    tokens = OutlookTokens.model_validate({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
    })
    if time.time() >= expires_at - 300:
        try:
            tokens = _refresh_outlook_tokens(refresh_token)
            _save_outlook_credentials(tokens)
        except Exception as error:
            logger.exception("Erreur refresh tokens Outlook: %s", error)
            return None
    return tokens


def _clear_outlook_credentials() -> None:
    """Supprime le fichier de tokens Outlook (déconnexion)."""
    path = _outlook_tokens_path()
    if path.exists():
        path.unlink()


def get_outlook_credentials() -> OutlookTokens | None:
    """Charge les tokens Outlook (access_token, etc.). À utiliser par l'OutlookAdapter."""
    return _load_outlook_credentials()
