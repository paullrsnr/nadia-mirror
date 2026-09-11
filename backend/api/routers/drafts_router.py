from fastapi import APIRouter, BackgroundTasks, Depends, File, Query, UploadFile

from backend.api.schemas import (
    DraftAttachmentResponse,
    DraftResponse,
    SaveDraftBody,
    SendDraftResponse,
)
from backend.core.services.draftService import DraftService
from backend.api.deps import get_draft_service

router = APIRouter(prefix="/drafts")


@router.get("/", response_model=list[DraftResponse])
def list_drafts(
    provider: str | None = Query(default=None, description="Provider (gmail, outlook)."),
    service: DraftService = Depends(get_draft_service),
):
    return service.list_drafts(provider)


@router.post("/{draft_id}", response_model=DraftResponse)
def save_draft(
    draft_id: str,
    payload: SaveDraftBody,
    service: DraftService = Depends(get_draft_service),
):
    return service.save_draft(draft_id, payload)


@router.post("/{draft_id}/send", response_model=SendDraftResponse)
def send_draft(
    draft_id: str,
    background_tasks: BackgroundTasks,
    service: DraftService = Depends(get_draft_service),
):
    result = service.send_draft(draft_id)
    if result.status == "success" and result.provider:
        background_tasks.add_task(service.refresh_sent_folder, result.provider)
    return result


@router.delete("/{draft_id}")
def delete_draft(draft_id: str, service: DraftService = Depends(get_draft_service)):
    service.delete_draft(draft_id)
    return {"status": "success"}


@router.post("/{draft_id}/attachments", response_model=DraftAttachmentResponse)
async def add_attachment(
    draft_id: str,
    file: UploadFile = File(...),
    service: DraftService = Depends(get_draft_service),
):
    content = await file.read()
    return service.add_attachment(draft_id, file.filename, content)


@router.delete("/{draft_id}/attachments/{attachment_id}")
def remove_attachment(
    draft_id: str,
    attachment_id: str,
    service: DraftService = Depends(get_draft_service),
):
    service.remove_attachment(draft_id, attachment_id)
    return {"status": "success"}
