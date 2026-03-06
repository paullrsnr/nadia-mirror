from pathlib import Path

from pydantic_settings import BaseSettings


class StorageSettings(BaseSettings):
    DATA_DIR: Path = Path.home() / ".nadia"
    SYNC_MIN_INTERVAL_MINUTES: int = 5

    def tokens_file(self, provider: str) -> Path:
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        return self.DATA_DIR / f"tokens_{provider.lower()}.json"
