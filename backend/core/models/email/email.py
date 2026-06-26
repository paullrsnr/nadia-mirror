from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

from backend.core.models.email.emailAddress import EmailAddress
from backend.core.models.email.emailAttachment import EmailAttachment
from backend.core.models.email.provider import Provider


@dataclass
class Email:
    id: str
    thread_id: str
    subject: str
    from_address: EmailAddress
    to_addresses: list[EmailAddress]
    date: datetime
    body_text: str
    provider: Provider
    cc_addresses: list[EmailAddress] = field(default_factory=list)
    bcc_addresses: list[EmailAddress] = field(default_factory=list)
    body_html: Optional[str] = None
    attachments: list[EmailAttachment] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    snippet: Optional[str] = None
    category: Optional[str] = None
    draft_reply: Optional[str] = None
    is_archived: bool = False
    pending_archive: bool = False
    is_starred: bool = False
    folder: str = "inbox"
