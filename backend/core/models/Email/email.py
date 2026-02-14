# pylint: disable=invalid-name
"""Modèle métier : email."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from backend.core.models.Email.emailAddress import EmailAddress
from backend.core.models.Email.emailAttachment import EmailAttachment


class Email(BaseModel):
    """Représentation métier d'un email."""

    id: str
    thread_id: str
    subject: str
    from_address: EmailAddress
    to_addresses: list[EmailAddress]
    date: datetime
    body_text: str
    cc_addresses: list[EmailAddress] = Field(default_factory=list)
    bcc_addresses: list[EmailAddress] = Field(default_factory=list)
    body_html: Optional[str] = None
    attachments: list[EmailAttachment] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    snippet: Optional[str] = None
    provider: Optional[str] = None  # gmail | outlook, pour archivage en vue "all"
