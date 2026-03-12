from typing import Literal, Optional

from pydantic import BaseModel


class ProviderSyncResponse(BaseModel):
    provider: str
    status: Literal["success", "error", "skipped"]
    message: Optional[str] = None
    synced: Optional[int] = None
    saved: Optional[int] = None
    timestamp: Optional[str] = None