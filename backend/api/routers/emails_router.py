from typing import Union

from fastapi import APIRouter, Depends, Query, HTTPException

from backend.api.deps import get_mailbox_service, get_emails_service, get_storage
from backend.adapters.bddProvider.sqlLite import SqliteStorageAdapter
from backend.api.schemas import EmailListResponse, ArchiveEmailResponse, SyncEmailsResponse
from backend.core.exceptions import AuthError, ProviderError
from backend.core.mailboxService import MailboxService
from backend.core.services.emailsService import EmailsService
from backend.core.models.email import SyncResult, SyncAllResult

router = APIRouter(prefix="/emails")


@router.get("/", response_model=EmailListResponse)
def list_emails(
    provider: str | None = Query(default=None, description="Provider (gmail, outlook, all)."),
    max_results: int = Query(default=50, ge=1, le=500),
    page: int = Query(default=1, ge=1),
    mailbox: MailboxService = Depends(get_mailbox_service),
):
    return mailbox.get_stored_emails(provider=provider, max_results=max_results, page=page)


@router.post("/archive/{email_id}", response_model=ArchiveEmailResponse)
def archive_email(
    email_id: str,
    provider: str | None = Query(default=None, description="Provider (gmail, outlook)."),
    service: EmailsService = Depends(get_emails_service),
):
    return service.archive_email(email_id, provider)


@router.get("/thread/{thread_id}")
def get_thread_emails(
    thread_id: str,
    storage: SqliteStorageAdapter = Depends(get_storage),
):
    emails = storage.find_emails_by_thread(thread_id)
    return {"emails": emails, "count": len(emails)}


@router.post("/sync", response_model=Union[SyncResult, SyncAllResult])
def sync_emails(
    provider: str | None = Query(default=None, description="Provider (gmail, outlook, all)."),
    max_results: int = Query(default=100, ge=1, le=500),
    mailbox: MailboxService = Depends(get_mailbox_service),
):
    return mailbox.sync_emails(provider=provider, max_results=max_results)
