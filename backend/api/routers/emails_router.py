from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend.adapters.gmailAdapter import GmailAdapter
from backend.core.mailboxService import MailboxService
from backend.api.schemas import Email, EmailThread, EmailListResponse
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
        emails, next_page_token = provider.get_emails(
            max_results=max_results,
            query=query,
            page_token=page_token,
        )
        
        return EmailListResponse(
            emails=emails,
            total=len(emails),
            page=1,  # TODO: Calculer la page réelle
            page_size=max_results,
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/emails/{email_id}", response_model=Email)
async def get_email(email_id: str):
    """Récupère un email spécifique"""
    try:
        provider = get_email_provider()
        return provider.get_email(email_id)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Email non trouvé: {str(e)}")


@router.get("/threads", response_model=list[EmailThread])
async def get_threads(
    max_results: int = Query(default=50, ge=1, le=500),
    query: Optional[str] = Query(default=None),
    page_token: Optional[str] = Query(default=None),
):
    """Récupère une liste de threads"""
    try:
        provider = get_email_provider()
        threads, next_page_token = provider.get_threads(
            max_results=max_results,
            query=query,
            page_token=page_token,
        )
        return threads
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/threads/{thread_id}", response_model=EmailThread)
async def get_thread(thread_id: str):
    """Récupère un thread spécifique"""
    try:
        provider = get_email_provider()
        return provider.get_thread(thread_id)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Thread non trouvé: {str(e)}")


@router.post("/emails/{email_id}/archive")
async def archive_email(email_id: str):
    """Archive un email"""
    try:
        provider = get_email_provider()
        success = provider.archive_email(email_id)
        return {"status": "success", "email_id": email_id} if success else {"status": "error"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.post("/emails/{email_id}/read")
async def mark_as_read(email_id: str):
    """Marque un email comme lu"""
    try:
        provider = get_email_provider()
        success = provider.mark_as_read(email_id)
        return {"status": "success", "email_id": email_id} if success else {"status": "error"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.post("/emails/send")
async def send_email(
    to: list[str],
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    thread_id: Optional[str] = None,
):
    """Envoie un email"""
    try:
        provider = get_email_provider()
        email_id = provider.send_email(
            to=to,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            thread_id=thread_id,
        )
        return {"status": "success", "email_id": email_id}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


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


@router.get("/emails/local", response_model=EmailListResponse)
async def get_local_emails(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    query: Optional[str] = Query(default=None),
):
    """Récupère les emails depuis le stockage local"""
    try:
        emails = mailbox_service.get_local_emails(limit=limit, offset=offset, query=query)
        return EmailListResponse(
            emails=emails,
            total=len(emails),
            page=(offset // limit) + 1,
            page_size=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
