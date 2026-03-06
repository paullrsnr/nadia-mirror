from dataclasses import dataclass
from datetime import datetime

from backend.core.models.Email.email import Email
from backend.core.models.Email.emailAddress import EmailAddress


@dataclass
class EmailThread:
    thread_id: str
    subject: str
    emails: list[Email]
    participants: list[EmailAddress]
    last_message_date: datetime
    unread_count: int = 0
