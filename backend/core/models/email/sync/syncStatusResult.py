from dataclasses import dataclass, field
from typing import Literal, Optional

from backend.core.models.email.sync.syncResult import SyncResult
from backend.core.models.email.sync.syncAllResult import SyncAllResult


@dataclass
class SyncStatusResult:
    status: Literal["running", "idle"]
    last_result: Optional[SyncResult | SyncAllResult] = field(default=None)
