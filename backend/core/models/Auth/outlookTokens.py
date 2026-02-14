# pylint: disable=invalid-name
"""Modèle métier : tokens OAuth Outlook (Microsoft Graph)."""
from pydantic import BaseModel


class OutlookTokens(BaseModel):
    """Tokens OAuth retournés par Microsoft (Graph)."""

    access_token: str
    refresh_token: str
    expires_at: float  # timestamp Unix
