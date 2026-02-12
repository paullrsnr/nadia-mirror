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
    """Config OAuth par provider (Gmail, Outlook, etc.)."""

    # Gmail
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI: str = "http://localhost:3333/auth/callback"
    GMAIL_SCOPES: list[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ]
    # Outlook (Microsoft Graph)
    OUTLOOK_CLIENT_ID: str = ""
    OUTLOOK_CLIENT_SECRET: str = ""
    OUTLOOK_REDIRECT_URI: str = "http://localhost:3333/auth/callback"
    OUTLOOK_TENANT: str = "common"
    OUTLOOK_SCOPES: list[str] = [
        "https://graph.microsoft.com/Mail.Read",
        "https://graph.microsoft.com/Mail.ReadWrite",
        "https://graph.microsoft.com/User.Read",
        "offline_access",
    ]
    # Commun (tous providers)
    FRONTEND_AUTH_CALLBACK_URL: str = "http://localhost:5173/auth/callback"


class StorageSettings(BaseSettings):
    """Config stockage local (credentials, DB, clés)."""

    DATA_DIR: Path = Path.home() / ".nadia"
    # Délai minimum entre deux syncs (minutes)
    SYNC_MIN_INTERVAL_MINUTES: int = 5

    def user_space_dir(self, user_space_id: str) -> Path:
        """Répertoire d’un espace utilisateur (BDD + tokens par espace = multi-utilisateurs)."""
        safe = user_space_id.strip().lower() or "default"
        if not safe.replace("_", "").isalnum():
            safe = "default"
        return self.DATA_DIR / "user_spaces" / safe

    def tokens_file(self, provider: str, user_space_id: str | None = None) -> Path:
        """Fichier de tokens pour un provider. user_space_id absent = espace courant."""
        if user_space_id is None:
            from backend.config.user_space import get_current_user_space_dir  # pylint: disable=import-outside-toplevel
            base = get_current_user_space_dir()
        else:
            base = self.user_space_dir(user_space_id)
        base.mkdir(parents=True, exist_ok=True)
        return base / f"tokens_{provider.lower()}.json"


class EmailSettings(BaseSettings):
    """Config email / provider."""

    # Provider d'email par défaut (permet de mutualiser Gmail, Outlook, etc. plus tard)
    DEFAULT_PROVIDER: str = "gmail"


class ApiSettings(BaseSettings):
    """Config serveur API."""

    API_PORT: int = 3333


# Instances par domaine : chaque module importe la sienne
auth_settings = AuthSettings()
storage_settings = StorageSettings()
email_settings = EmailSettings()
api_settings = ApiSettings()
