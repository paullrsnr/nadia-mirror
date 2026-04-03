import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.api.deps import get_auto_archive_service, get_storage
from backend.adapters.bddProvider.sqlLite import SqliteStorageAdapter
from backend.adapters.bddProvider.sqlLite.models.autoArchiveConfig import AutoArchiveConfig
from backend.core.services.autoArchiveService import AutoArchiveService

router = APIRouter(prefix="/auto-archive", tags=["auto-archive"])

_SETTING_KEY = "auto_archive_rules"


class RulesPayload(BaseModel):
    rules: str


@router.get("/rules", response_model=AutoArchiveConfig)
def get_rules(storage: SqliteStorageAdapter = Depends(get_storage)):
    raw = storage.get_setting(_SETTING_KEY)
    if raw is None:
        return AutoArchiveConfig(rules="", enabled=False)
    data = json.loads(raw)
    return AutoArchiveConfig(rules=data["rules"], enabled=data["enabled"])


@router.post("/rules", response_model=AutoArchiveConfig)
def save_rules(payload: RulesPayload, storage: SqliteStorageAdapter = Depends(get_storage)):
    config = AutoArchiveConfig(rules=payload.rules, enabled=bool(payload.rules.strip()))
    storage.set_setting(
        _SETTING_KEY,
        json.dumps({"rules": config.rules, "enabled": config.enabled}, ensure_ascii=False),
    )
    return config


@router.get("/pending")
def get_pending(service: AutoArchiveService = Depends(get_auto_archive_service)):
    emails = service.get_pending()
    return {"emails": emails, "count": len(emails)}


@router.post("/confirm/{email_id}")
def confirm_archive(email_id: str, service: AutoArchiveService = Depends(get_auto_archive_service)):
    service.confirm_archive(email_id)
    return {"email_id": email_id, "status": "archived"}


@router.post("/reject/{email_id}")
def reject_archive(email_id: str, service: AutoArchiveService = Depends(get_auto_archive_service)):
    service.reject_archive(email_id)
    return {"email_id": email_id, "status": "kept"}
