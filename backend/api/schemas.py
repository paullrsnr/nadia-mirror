"""Schémas Pydantic pour l'API."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuthUrlResponse(BaseModel):
    """Réponse contenant l'URL d'authentification OAuth."""

    auth_url: str


# AuthCallbackRequest - À implémenter


class AuthStatusResponse(BaseModel):
    """Réponse contenant le statut d'authentification."""

    is_authenticated: bool
    email: Optional[str] = None


class EmailAddress(BaseModel):
    """Représentation d'une adresse email."""

    name: Optional[str] = None
    email: str


class EmailAttachment(BaseModel):
    """Représentation d'une pièce jointe."""

    filename: str
    mime_type: str
    size: int
    attachment_id: str


class Email(BaseModel):
    """Représentation d'un email."""

    id: str
    thread_id: str
    subject: str
    from_address: EmailAddress
    to_addresses: list[EmailAddress]
    cc_addresses: list[EmailAddress] = []
    bcc_addresses: list[EmailAddress] = []
    date: datetime
    body_text: str
    body_html: Optional[str] = None
    attachments: list[EmailAttachment] = []
    labels: list[str] = []
    snippet: Optional[str] = None


class EmailThread(BaseModel):
    """Représentation d'un fil de discussion email."""

    thread_id: str
    subject: str
    emails: list[Email]
    participants: list[EmailAddress]
    last_message_date: datetime
    unread_count: int = 0


class EmailListResponse(BaseModel):
    """Réponse contenant une liste d'emails paginée."""

    emails: list[Email]
    total: int
    page: int
    page_size: int
