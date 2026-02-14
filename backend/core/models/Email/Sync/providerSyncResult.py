# pylint: disable=invalid-name
"""Modèle métier : résultat de sync pour un provider (utilisé dans sync "all")."""
from typing import Literal, Optional
from pydantic import BaseModel


class ProviderSyncResult(BaseModel):
    """Résultat de sync pour un provider (utilisé dans sync "all")."""

    provider: str
    status: Literal["success", "error", "skipped"]
    message: Optional[str] = None
    synced: Optional[int] = None
    saved: Optional[int] = None
    timestamp: Optional[str] = None
