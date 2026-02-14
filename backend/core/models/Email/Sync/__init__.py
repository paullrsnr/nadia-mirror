"""Modèles métier du domaine synchronisation d'emails (core)."""
from backend.core.models.Email.Sync.syncResult import SyncResult
from backend.core.models.Email.Sync.providerSyncResult import ProviderSyncResult
from backend.core.models.Email.Sync.syncAllResult import SyncAllResult

__all__ = [
    "SyncResult",
    "ProviderSyncResult",
    "SyncAllResult",
]
