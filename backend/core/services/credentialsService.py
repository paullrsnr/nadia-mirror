# pylint: disable=invalid-name
"""Stockage des credentials OAuth par provider (Gmail, Outlook ; extensible)."""
import json
import logging
import os
import time

import httpx

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from backend.config.settings import storage_settings, auth_settings
from backend.utils.encryption import decrypt_data, encrypt_data

logger = logging.getLogger(__name__)

# Providers supportés (extensible)
PROVIDER_GMAIL = "gmail"
PROVIDER_OUTLOOK = "outlook"


def _gmail_tokens_path() -> os.PathLike:
    """Chemin du fichier de tokens Gmail."""
    return storage_settings.tokens_file(PROVIDER_GMAIL)


def _save_gmail_credentials(credentials: Credentials) -> None:
    """Sauvegarde les credentials OAuth Google (Gmail) — chiffrement des champs sensibles."""
    path = _gmail_tokens_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    creds_dict = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    encrypted_dict = {
        "token": encrypt_data(creds_dict["token"]) if creds_dict["token"] else None,
        "refresh_token": (
            encrypt_data(creds_dict["refresh_token"])
            if creds_dict["refresh_token"]
            else None
        ),
        "token_uri": creds_dict["token_uri"],
        "client_id": creds_dict["client_id"],
        "client_secret": (
            encrypt_data(creds_dict["client_secret"])
            if creds_dict["client_secret"]
            else None
        ),
        "scopes": creds_dict["scopes"],
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(encrypted_dict, f)

    os.chmod(path, 0o600)


def _load_gmail_credentials() -> Credentials | None:
    """Charge les credentials OAuth Google (Gmail) — déchiffrement et refresh si expiré."""
    path = _gmail_tokens_path()
    # Compat: ancien fichier unique tokens.json
    if not path.exists():
        legacy = storage_settings.DATA_DIR / "tokens.json"
        if legacy.exists():
            path = legacy
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            encrypted_dict = json.load(f)

        creds_dict = {
            "token": (
                decrypt_data(encrypted_dict["token"])
                if encrypted_dict.get("token")
                else None
            ),
            "refresh_token": (
                decrypt_data(encrypted_dict["refresh_token"])
                if encrypted_dict.get("refresh_token")
                else None
            ),
            "token_uri": encrypted_dict.get("token_uri"),
            "client_id": encrypted_dict.get("client_id"),
            "client_secret": (
                decrypt_data(encrypted_dict["client_secret"])
                if encrypted_dict.get("client_secret")
                else None
            ),
            "scopes": encrypted_dict.get("scopes", []),
        }

        credentials = Credentials(
            token=creds_dict.get("token"),
            refresh_token=creds_dict.get("refresh_token"),
            token_uri=creds_dict.get("token_uri"),
            client_id=creds_dict.get("client_id"),
            client_secret=creds_dict.get("client_secret"),
            scopes=creds_dict.get("scopes"),
        )

        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            _save_gmail_credentials(credentials)

        return credentials
    except Exception as error:
        logger.exception("Erreur lors du chargement des credentials Gmail: %s", error)
        return None


def _clear_gmail_credentials() -> None:
    """Supprime le fichier de tokens Gmail (déconnexion)."""
    path = _gmail_tokens_path()
    if path.exists():
        path.unlink()


# --- Outlook (Microsoft OAuth) ---


def _outlook_tokens_path() -> os.PathLike:
    """Chemin du fichier de tokens Outlook."""
    return storage_settings.tokens_file(PROVIDER_OUTLOOK)


def _save_outlook_credentials(tokens: dict) -> None:
    """Sauvegarde les tokens Outlook (access_token, refresh_token, expires_at)."""
    path = _outlook_tokens_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tokens, f)
    os.chmod(path, 0o600)


def _refresh_outlook_tokens(refresh_token: str) -> dict:
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
    return {
        "access_token": body["access_token"],
        "refresh_token": body.get("refresh_token") or refresh_token,
        "expires_at": time.time() + expires_in,
    }


def _load_outlook_credentials() -> dict | None:
    """Charge les tokens Outlook ; refresh si expirés (marge 5 min)."""
    path = _outlook_tokens_path()
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            tokens = json.load(f)
    except Exception as error:
        logger.exception("Erreur chargement tokens Outlook: %s", error)
        return None
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    if not access_token or not refresh_token:
        return None
    expires_at = tokens.get("expires_at", 0)
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


# --- Dispatcher par provider (extensible) ---


def save_credentials(credentials: Credentials | dict, provider: str) -> None:
    """Sauvegarde les credentials pour le provider (Gmail: Credentials, Outlook: dict)."""
    resolved = provider.lower()
    if resolved == PROVIDER_GMAIL:
        _save_gmail_credentials(credentials)
        return
    if resolved == PROVIDER_OUTLOOK:
        if isinstance(credentials, dict):
            _save_outlook_credentials(credentials)
            return
        raise TypeError("Outlook attend un dict de tokens")
    raise ValueError(f"Provider credentials non supporté: {resolved}")


def load_credentials(provider: str) -> Credentials | dict | None:
    """Charge les credentials pour le provider (Gmail: Credentials, Outlook: dict)."""
    resolved = provider.lower()
    if resolved == PROVIDER_GMAIL:
        return _load_gmail_credentials()
    if resolved == PROVIDER_OUTLOOK:
        return _load_outlook_credentials()
    raise ValueError(f"Provider credentials non supporté: {resolved}")


def clear_credentials(provider: str) -> None:
    """Supprime les credentials pour le provider."""
    resolved = provider.lower()
    if resolved == PROVIDER_GMAIL:
        _clear_gmail_credentials()
        return
    if resolved == PROVIDER_OUTLOOK:
        _clear_outlook_credentials()
        return
    raise ValueError(f"Provider credentials non supporté: {resolved}")


def get_gmail_credentials() -> Credentials | None:
    """Charge les credentials Gmail. À utiliser par le GmailAdapter."""
    return _load_gmail_credentials()


def get_outlook_credentials() -> dict | None:
    """Charge les tokens Outlook (access_token, etc.). À utiliser par l'OutlookAdapter."""
    return _load_outlook_credentials()
