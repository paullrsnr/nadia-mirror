from typing import Union

from fastapi import APIRouter, Depends, Query, HTTPException

from backend.api.deps import get_mailbox_service, get_emails_service
from backend.api.schemas import EmailListResponse, ArchiveEmailResponse, SyncEmailsResponse
from backend.core.exceptions import AuthError, ProviderError
from backend.core.mailboxService import MailboxService
from backend.core.services.emailsService import EmailsService
from backend.core.models.Email import SyncResult, SyncAllResult

router = APIRouter(prefix="/emails")


@router.get("/", response_model=EmailListResponse)
async def list_emails(
    provider: str | None = Query(default=None, description="Provider (gmail, outlook, all)."),
    max_results: int = Query(default=50, ge=1, le=500),
    page: int = Query(default=1, ge=1),
    mailbox: MailboxService = Depends(get_mailbox_service),
):
    return mailbox.get_stored_emails(provider=provider, max_results=max_results, page=page)


@router.post("/archive/{email_id}", response_model=ArchiveEmailResponse)
async def archive_email(
    email_id: str,
    provider: str | None = Query(default=None, description="Provider (gmail, outlook)."),
    service: EmailsService = Depends(get_emails_service),
):
    try:
        return service.archive_email(email_id, provider)
    except ProviderError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@router.post("/sync", response_model=Union[SyncResult, SyncAllResult])
async def sync_emails(
    provider: str | None = Query(default=None, description="Provider (gmail, outlook, all)."),
    max_results: int = Query(default=100, ge=1, le=500),
    mailbox: MailboxService = Depends(get_mailbox_service),
):
    try:
        return mailbox.sync_emails(provider=provider, max_results=max_results)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except ProviderError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
