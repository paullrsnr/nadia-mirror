from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.api.deps import get_auto_archive_service
from backend.adapters.bddProvider.sqlLite.models.autoArchiveConfig import AutoArchiveConfig
from backend.core.services.autoArchiveService import AutoArchiveService

router = APIRouter(prefix="/auto-archive", tags=["auto-archive"])


class RulesPayload(BaseModel):
    rules: str


@router.get("/rules", response_model=AutoArchiveConfig)
def get_rules(service: AutoArchiveService = Depends(get_auto_archive_service)):
    return service.get_rules()


@router.post("/rules", response_model=AutoArchiveConfig)
def save_rules(payload: RulesPayload, service: AutoArchiveService = Depends(get_auto_archive_service)):
    return service.save_rules(payload.rules)


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
