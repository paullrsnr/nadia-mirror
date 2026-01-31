# pylint: disable=invalid-name
"""Service de gestion des credentials OAuth (sauvegarde, chargement, chiffrement)."""
import json
import logging
import os

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from backend.config.settings import storage_settings
from backend.utils.encryption import decrypt_data, encrypt_data

logger = logging.getLogger(__name__)


def save_credentials(credentials: Credentials) -> None:
    """Sauvegarde les credentials de manière sécurisée (chiffrement des champs sensibles)."""
    storage_settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

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

    with open(storage_settings.TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(encrypted_dict, f)

    os.chmod(storage_settings.TOKENS_FILE, 0o600)


def load_credentials() -> Credentials | None:
    """Charge les credentials sauvegardés (déchiffrement + refresh si expiré)."""
    if not storage_settings.TOKENS_FILE.exists():
        return None

    try:
        with open(storage_settings.TOKENS_FILE, "r", encoding="utf-8") as f:
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
            save_credentials(credentials)

        return credentials
    except Exception as e:
        logger.exception("Erreur lors du chargement des credentials: %s", e)
        return None


def clear_credentials() -> None:
    """Supprime le fichier de tokens (déconnexion)."""
    if storage_settings.TOKENS_FILE.exists():
        storage_settings.TOKENS_FILE.unlink()


# Alias pour les modules qui ont besoin de charger les credentials (ex: GmailAdapter)
get_credentials = load_credentials
