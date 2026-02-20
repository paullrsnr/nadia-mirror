"""Routeur emails : liste, archivage, synchronisation (délègue aux services)."""
from typing import Union

from fastapi import APIRouter, Query

from backend.api.schemas import (
    EmailListResponse,
    ArchiveEmailResponse,
    SyncEmailsResponse,
)
from backend.core.services.email.emailsService import EmailsService
from backend.core.mailboxService import MailboxService
from backend.core.models.Email import SyncResult, SyncAllResult

router = APIRouter(prefix="/emails")


@router.get("/", response_model=EmailListResponse)
async def list_emails(
    provider: str | None = Query(default=None, description="Provider (gmail, outlook, all). Défaut : gmail."),
    max_results: int = Query(default=50, ge=1, le=500),
    page: int = Query(default=1, ge=1),
):
    """Liste les emails depuis le stockage local. Filtre : ?provider=gmail | outlook | all."""
    mailbox = MailboxService()
    return mailbox.get_stored_emails(
        provider=provider,
        max_results=max_results,
        page=page,
    )


@router.post("/archive/{email_id}", response_model=ArchiveEmailResponse)
async def archive_email(
    email_id: str,
    provider: str | None = Query(default=None, description="Provider (gmail, outlook). Défaut : gmail."),
):
    """Archive un email. Requiert ?provider=gmail ou ?provider=outlook."""
    service = EmailsService()
    return service.archive_email(email_id, provider)


@router.post("/sync", response_model=Union[SyncResult, SyncAllResult])
async def sync_emails(
    provider: str | None = Query(default=None, description="Provider (gmail, outlook, all). Défaut : gmail."),
    max_results: int = Query(default=100, ge=1, le=500),
):
    """Synchronise les non lus vers le stockage local. Si provider=all, synchronise Gmail puis Outlook."""
    mailbox = MailboxService()
    return mailbox.sync_emails(provider=provider, max_results=max_results)
