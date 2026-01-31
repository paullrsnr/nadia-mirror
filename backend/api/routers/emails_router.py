"""Routeur emails : délègue aux services, ne fait que le routing."""
from fastapi import APIRouter, HTTPException, Query

from backend.api.schemas import EmailListResponse
from backend.api.dependencies import get_email_provider
from backend.core.services.emailsService import EmailsService
from backend.core.mailboxService import MailboxService

router = APIRouter(prefix="/emails")


@router.get("/", response_model=EmailListResponse)
async def get_emails(
    max_results: int = Query(default=50, ge=1, le=500),
    page: int = Query(default=1, ge=1),
):
    """Récupère la liste d'emails depuis le stockage local (SQLite).

    Les emails affichés sont ceux déjà synchronisés ; pas d'appel Gmail ici.
    """
    try:
        provider = get_email_provider()
        result = MailboxService(provider).get_stored_emails(
            max_results=max_results,
            page=page,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{email_id}/archive")
async def archive_email(email_id: str):
    """Archive un email."""
    try:
        provider = get_email_provider()
        success = EmailsService(provider).archive_email(email_id)
        return (
            {"status": "success", "email_id": email_id}
            if success
            else {"status": "error"}
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/sync")
async def sync_emails(
    max_results: int = Query(default=100, ge=1, le=500),
):
    """Synchronise les derniers non lus vers le stockage local.

    Le backend gère le délai (pas de sync si dernière sync < SYNC_MIN_INTERVAL_MINUTES).
    """
    try:
        provider = get_email_provider()
        result = MailboxService(provider).sync_emails(max_results=max_results)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
