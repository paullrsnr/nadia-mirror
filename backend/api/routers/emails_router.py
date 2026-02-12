"""Routeur emails : liste, archivage, synchronisation (délègue aux services)."""
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.api.schemas import EmailListResponse
from backend.api.dependencies import get_email_adapter, get_provider_for_archive, get_provider_for_list
from backend.core.services.connectionOrchestrator import get_connection_credentials
from backend.core.services.emailsService import EmailsService
from backend.core.mailboxService import MailboxService

router = APIRouter(prefix="/emails")


@router.get("/", response_model=EmailListResponse)
async def list_emails(
    max_results: int = Query(default=50, ge=1, le=500),
    page: int = Query(default=1, ge=1),
    provider: str = Depends(get_provider_for_list),
):
    """Liste les emails depuis le stockage local. Filtre : ?provider=gmail | outlook | all."""
    mailbox = MailboxService()
    return mailbox.get_stored_emails(
        provider=provider,
        max_results=max_results,
        page=page,
    )


@router.post("/archive/{email_id}")
async def archive_email(
    email_id: str,
    provider: str = Depends(get_provider_for_archive),
):
    """Archive un email. Requiert ?provider=gmail ou ?provider=outlook."""
    adapter = get_email_adapter(provider)
    return EmailsService(adapter).archive_email_response(email_id)


@router.post("/sync")
async def sync_emails(
    max_results: int = Query(default=100, ge=1, le=500),
    provider: str = Depends(get_provider_for_list),
):
    """Synchronise les non lus vers le stockage local. Si provider=all, synchronise Gmail puis Outlook."""
    mailbox = MailboxService()

    if provider == "all":
        sync_results = []
        for provider_key in ("gmail", "outlook"):
            credentials = get_connection_credentials(provider_key)
            if not credentials:
                continue
            adapter = get_email_adapter(provider_key)
            sync_result = mailbox.sync_emails(
                adapter,
                provider_tag=provider_key,
                max_results=max_results,
                skip_cooldown=True,
            )
            sync_results.append({"provider": provider_key, **sync_result})
        if not sync_results:
            raise HTTPException(status_code=401, detail="Aucune boîte connectée")
        mailbox.update_last_sync_time()
        return {"status": "success", "results": sync_results}

    adapter = get_email_adapter(provider)
    return mailbox.sync_emails(adapter, provider_tag=provider, max_results=max_results)