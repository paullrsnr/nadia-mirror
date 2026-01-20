from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI: str = "http://localhost:3333/auth/callback"
    
    # Scopes Gmail
    GMAIL_SCOPES: list[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ]
    
    # Storage
    DATA_DIR: Path = Path.home() / ".nadia"
    TOKENS_FILE: Path = DATA_DIR / "tokens.json"
    
    # API
    API_PORT: int = 3333
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
