"""
Config par domaine : chaque module n'importe que ce dont il a besoin.
Un seul .env chargé une fois.
"""
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Chargement du .env une seule fois
BACKEND_DIR = Path(__file__).parent.parent
load_dotenv(BACKEND_DIR / ".env")


class AuthSettings(BaseSettings):
    """Config OAuth / Gmail (auth, callback)."""

    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI: str = "http://localhost:3333/auth/callback"
    FRONTEND_AUTH_CALLBACK_URL: str = "http://localhost:5173/auth/callback"
    GMAIL_SCOPES: list[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ]


class StorageSettings(BaseSettings):
    """Config stockage local (credentials, DB, clés)."""

    DATA_DIR: Path = Path.home() / ".nadia"
    # Délai minimum entre deux syncs (minutes) — le backend refuse de re-sync avant
    SYNC_MIN_INTERVAL_MINUTES: int = 5

    @property
    def TOKENS_FILE(self) -> Path:
        return self.DATA_DIR / "tokens.json"


class ApiSettings(BaseSettings):
    """Config serveur API."""

    API_PORT: int = 3333


# Instances par domaine : chaque module importe la sienne
auth_settings = AuthSettings()
storage_settings = StorageSettings()
api_settings = ApiSettings()
