"""Configuration stockage local (credentials, DB, clés)."""
from pathlib import Path

from pydantic_settings import BaseSettings


class StorageSettings(BaseSettings):
    """Config stockage local (credentials, DB, clés)."""

    DATA_DIR: Path = Path.home() / ".nadia"
    # Délai minimum entre deux syncs (minutes)
    SYNC_MIN_INTERVAL_MINUTES: int = 5

    def tokens_file(self, provider: str) -> Path:
        """Fichier de tokens pour un provider."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        return self.DATA_DIR / f"tokens_{provider.lower()}.json"
