"""Configuration serveur API."""
from pydantic_settings import BaseSettings


class ApiSettings(BaseSettings):
    """Config serveur API."""

    API_PORT: int = 3333
