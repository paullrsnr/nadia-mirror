# pylint: disable=invalid-name
"""Modèles métier du domaine email (core). Pas de dépendance à Pydantic."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class EmailAddress:
    """Représentation métier d'une adresse email."""

    email: str
    name: Optional[str] = None


@dataclass
class EmailAttachment:
    """Représentation métier d'une pièce jointe."""

    filename: str
    mime_type: str
    size: int
    attachment_id: str


@dataclass
class Email:
    """Représentation métier d'un email."""

    id: str
    thread_id: str
    subject: str
    from_address: EmailAddress
    to_addresses: list[EmailAddress]
    date: datetime
    body_text: str
    cc_addresses: list[EmailAddress] = field(default_factory=list)
    bcc_addresses: list[EmailAddress] = field(default_factory=list)
    body_html: Optional[str] = None
    attachments: list[EmailAttachment] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    snippet: Optional[str] = None


@dataclass
class EmailThread:
    """Représentation métier d'un fil de discussion email."""

    thread_id: str
    subject: str
    emails: list[Email]
    participants: list[EmailAddress]
    last_message_date: datetime
    unread_count: int = 0


@dataclass
class EmailListResult:
    """Résultat métier d'une liste d'emails paginée."""

    emails: list[Email]
    total: int
    page: int
    page_size: int
