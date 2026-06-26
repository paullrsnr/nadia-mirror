from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

from backend.core.models.email.emailAddress import EmailAddress
from backend.core.models.email.emailAttachment import EmailAttachment


@dataclass
class DraftEmail:
    id: str
    provider: str
    to_addresses: list[EmailAddress]
    subject: str
    body_text: str
    updated_at: datetime
    cc_addresses: list[EmailAddress] = field(default_factory=list)
    bcc_addresses: list[EmailAddress] = field(default_factory=list)
    in_reply_to_email_id: Optional[str] = None
    attachments: list[EmailAttachment] = field(default_factory=list)
    body_html: Optional[str] = None
