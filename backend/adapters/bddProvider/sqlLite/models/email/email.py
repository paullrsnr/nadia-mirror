from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from backend.core.models.email.emailAddress import EmailAddress
from backend.core.models.email.emailAttachment import EmailAttachment
from backend.core.models.email.provider import Provider


class Email(BaseModel):
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
    provider: Provider
