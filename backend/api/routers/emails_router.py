from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend.adapters.gmailAdapter import GmailAdapter
from backend.core.mailboxService import MailboxService
from backend.api.schemas import EmailListResponse
from backend.api.routers.auth_router import get_credentials

router = APIRouter()
mailbox_service = MailboxService()


def get_email_provider():
    """Récupère le provider d'email (Gmail)"""
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="Non authentifié")

    return GmailAdapter()


@router.get("/emails", response_model=EmailListResponse)
async def get_emails(
    max_results: int = Query(default=50, ge=1, le=500),
    query: Optional[str] = Query(default=None),
    page_token: Optional[str] = Query(default=None),
):
    """Récupère une liste d'emails"""
    try:
        provider = get_email_provider()
        emails, _ = provider.get_emails(
            max_results=max_results,
            query=query,
            page_token=page_token,
        )

        return EmailListResponse(
            emails=emails,
            total=len(emails),
            page=1,
            page_size=max_results,
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# GET /emails/{email_id} - À implémenter

# GET /threads - À implémenter

# GET /threads/{thread_id} - À implémenter


@router.post("/emails/{email_id}/archive")
async def archive_email(email_id: str):
    """Archive un email"""
    try:
        provider = get_email_provider()
        success = provider.archive_email(email_id)
        return (
            {"status": "success", "email_id": email_id}
            if success
            else {"status": "error"}
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# POST /emails/{email_id}/read - À implémenter


@router.post("/emails/sync")
async def sync_emails(
    max_results: int = Query(default=100, ge=1, le=500),
    force: bool = Query(default=False),
):
    """Synchronise les emails depuis Gmail vers le stockage local"""
    try:
        result = mailbox_service.sync_emails(max_results=max_results, force=force)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
