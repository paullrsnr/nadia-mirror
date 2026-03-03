# pylint: disable=invalid-name
"""Stockage des tokens OAuth Outlook : sauvegarde/chargement/suppression/refresh sur disque."""
import json
import logging
import os
import time

import httpx

from backend.config.settings import storage_settings, auth_settings
from backend.core.models.Email import Provider
from backend.adapters.AuthProvider.Outlook.outlookTokens import OutlookTokens

logger = logging.getLogger(__name__)

_PROVIDER = Provider.OUTLOOK.value


def _tokens_path() -> os.PathLike:
    return storage_settings.tokens_file(_PROVIDER)


def save_outlook_credentials(tokens: OutlookTokens) -> None:
    """Sauvegarde les tokens Outlook sur disque."""
    path = _tokens_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tokens.model_dump(), f)
    os.chmod(path, 0o600)


def _refresh_tokens(refresh_token: str) -> OutlookTokens:
    """Échange le refresh_token contre de nouveaux tokens (Microsoft token endpoint)."""
    url = f"https://login.microsoftonline.com/{auth_settings.OUTLOOK_TENANT}/oauth2/v2.0/token"
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


def load_outlook_credentials() -> OutlookTokens | None:
    """Charge les tokens Outlook depuis le disque ; refresh automatique si expirés (marge 5 min)."""
    path = _tokens_path()
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as error:
        logger.exception("Erreur chargement tokens Outlook: %s", error)
        return None

    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    if not access_token or not refresh_token:
        return None

    tokens = OutlookTokens(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=data.get("expires_at", 0),
    )

    if time.time() >= tokens.expires_at - 300:
        try:
            tokens = _refresh_tokens(refresh_token)
            save_outlook_credentials(tokens)
        except Exception as error:
            logger.exception("Erreur refresh tokens Outlook: %s", error)
            return None

    return tokens


def clear_outlook_credentials() -> None:
    """Supprime le fichier de tokens Outlook (déconnexion)."""
    path = _tokens_path()
    if path.exists():
        path.unlink()


def get_outlook_credentials() -> OutlookTokens | None:
    """Point d'entrée public pour les adapters mail (OutlookAdapter)."""
    return load_outlook_credentials()


# Alias privés attendus par config/Credential/outlookCredentialProvider (imports lazy)
_save_outlook_credentials = save_outlook_credentials
_load_outlook_credentials = load_outlook_credentials
_clear_outlook_credentials = clear_outlook_credentials
