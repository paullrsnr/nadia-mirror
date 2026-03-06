from typing import Literal
from pydantic import BaseModel

from backend.core.models.Email.Sync.providerSyncResult import ProviderSyncResult


class SyncAllResult(BaseModel):
    status: Literal["success"]
    results: list[ProviderSyncResult]
