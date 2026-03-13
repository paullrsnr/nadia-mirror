from typing import Literal, Optional
from dataclasses import dataclass


@dataclass
class SyncResult:
    status: Literal["success", "error", "skipped"]
    message: Optional[str] = None
    synced: Optional[int] = None
    saved: Optional[int] = None
    timestamp: Optional[str] = None
    last_sync: Optional[str] = None
