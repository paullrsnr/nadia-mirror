import json
import logging
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from backend.config.settings import storage_settings
from backend.core.models.Email import Provider
from backend.utils.encryption import decrypt_data, encrypt_data

logger = logging.getLogger(__name__)

def save_gmail_credentials(credentials: Credentials) -> None:
    path = storage_settings.tokens_file(Provider.GMAIL.value)
    path.parent.mkdir(parents=True, exist_ok=True)

    encrypted = {
        "token": encrypt_data(credentials.token) if credentials.token else None,
        "refresh_token": (
            encrypt_data(credentials.refresh_token) if credentials.refresh_token else None
        ),
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": (
            encrypt_data(credentials.client_secret) if credentials.client_secret else None
        ),
        "scopes": list(credentials.scopes) if credentials.scopes else [],
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(encrypted, f)

    os.chmod(path, 0o600)


def load_gmail_credentials() -> Credentials | None:
    path = storage_settings.tokens_file(Provider.GMAIL.value)

    if not path.exists():
        legacy = storage_settings.DATA_DIR / "tokens.json"
        if legacy.exists():
            path = legacy

    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        credentials = Credentials(
            token=decrypt_data(data["token"]) if data.get("token") else None,
            refresh_token=(
                decrypt_data(data["refresh_token"]) if data.get("refresh_token") else None
            ),
            token_uri=data.get("token_uri"),
            client_id=data.get("client_id"),
            client_secret=(
                decrypt_data(data["client_secret"]) if data.get("client_secret") else None
            ),
            scopes=data.get("scopes", []),
        )

        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            save_gmail_credentials(credentials)

        return credentials
    except Exception as error:
        logger.exception("Erreur lors du chargement des credentials Gmail: %s", error)
        return None


def clear_gmail_credentials() -> None:
    path = storage_settings.tokens_file(Provider.GMAIL.value)
    if path.exists():
        path.unlink()


def get_gmail_credentials() -> Credentials | None:
    return load_gmail_credentials()

