from typing import Literal, Optional
from pydantic import BaseModel


class SyncResult(BaseModel):
    status: Literal["success", "error", "skipped"]
    message: Optional[str] = None
    synced: Optional[int] = None  # Nombre d'emails récupérés
    saved: Optional[int] = None  # Nombre d'emails enregistrés
    timestamp: Optional[str] = None  # ISO 8601
    last_sync: Optional[str] = None  # ISO 8601 (pour status=skipped)
