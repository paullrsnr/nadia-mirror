# pylint: disable=invalid-name
"""Modèle métier : résultat de synchronisation multi-provider (all)."""
from typing import Literal
from pydantic import BaseModel

from backend.core.models.Email.Sync.providerSyncResult import ProviderSyncResult


class SyncAllResult(BaseModel):
    """Résultat de synchronisation multi-provider (all)."""

    status: Literal["success"]
    results: list[ProviderSyncResult]
