"""Configuration email / provider."""
from pydantic_settings import BaseSettings

from backend.config.providers import DEFAULT_PROVIDER as _DEFAULT_PROVIDER


class EmailSettings(BaseSettings):
    """Config email / provider."""

    # Provider d'email par défaut (importe depuis providers.py pour cohérence)
    DEFAULT_PROVIDER: str = _DEFAULT_PROVIDER
