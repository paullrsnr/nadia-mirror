import json
import logging
import os
import time

import httpx

from backend.config.settings import storage_settings, auth_settings
from backend.core.models.email import Provider
from backend.adapters.authProvider.Outlook.outlookTokens import OutlookTokens

logger = logging.getLogger(__name__)


def save_outlook_credentials(tokens: OutlookTokens) -> None:
    path = storage_settings.tokens_file(Provider.OUTLOOK.value)

    response = open(path, "w", encoding="utf-8")
    json.dump(tokens.model_dump(), response)
    response.close()

    os.chmod(path, 0o600)


def load_outlook_credentials() -> OutlookTokens | None:
    path = storage_settings.tokens_file(Provider.OUTLOOK.value)
    if not path.exists():
        return None

    try:
        response = open(path, "r", encoding="utf-8")
        data = json.load(response)
        response.close()
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
        expires_at_timestamp=data.get("expires_at_timestamp", 0),
    )

    if time.time() >= tokens.expires_at_timestamp - 300:
        try:
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
            tokens = OutlookTokens(
                access_token=body["access_token"],
                refresh_token=body.get("refresh_token") or refresh_token,
                expires_at_timestamp=time.time() + int(body.get("expires_in", 3600)),
            )
            save_outlook_credentials(tokens)
        except Exception as error:
            logger.exception("Erreur refresh tokens Outlook: %s", error)
            return None
    return tokens


def clear_outlook_credentials() -> None:
    path = storage_settings.tokens_file(Provider.OUTLOOK.value)
    if path.exists():
        path.unlink()
