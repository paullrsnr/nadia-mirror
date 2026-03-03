"""Configuration du provider email par défaut."""
from pydantic_settings import BaseSettings


class EmailSettings(BaseSettings):
    DEFAULT_PROVIDER: str = "gmail"
