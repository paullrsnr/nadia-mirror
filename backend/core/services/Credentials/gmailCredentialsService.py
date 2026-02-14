# pylint: disable=invalid-name
"""Gestion des credentials OAuth Gmail (sauvegarde, chargement, suppression)."""
import json
import logging
import os

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from backend.config.settings import storage_settings
from backend.config.providers import EmailProvider
from backend.utils.encryption import decrypt_data, encrypt_data

logger = logging.getLogger(__name__)

PROVIDER_GMAIL = EmailProvider.GMAIL.value


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


def get_gmail_credentials() -> Credentials | None:
    """Charge les credentials Gmail. À utiliser par le GmailAdapter."""
    return _load_gmail_credentials()
