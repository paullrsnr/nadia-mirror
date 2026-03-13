from typing import Literal, Optional
from dataclasses import dataclass


@dataclass
class ProviderSyncResult:
    provider: str
    status: Literal["success", "error", "skipped"]
    message: Optional[str] = None
    synced: Optional[int] = None
    saved: Optional[int] = None
    timestamp: Optional[str] = None
