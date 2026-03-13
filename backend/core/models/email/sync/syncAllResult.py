from typing import Literal
from dataclasses import dataclass

from backend.core.models.email.sync.providerSyncResult import ProviderSyncResult


@dataclass
class SyncAllResult:
    status: Literal["success"]
    results: list[ProviderSyncResult]
