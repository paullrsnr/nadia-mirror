"""Modèle : tokens OAuth Microsoft (accès + refresh + expiration)."""
from pydantic import BaseModel


class OutlookTokens(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: float  # timestamp Unix
