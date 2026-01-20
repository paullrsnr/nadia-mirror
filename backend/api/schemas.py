from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuthUrlResponse(BaseModel):
    auth_url: str


class AuthCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None


class AuthStatusResponse(BaseModel):
    is_authenticated: bool
    email: Optional[str] = None


class EmailAddress(BaseModel):
    name: Optional[str] = None
    email: str


class EmailAttachment(BaseModel):
    filename: str
    mime_type: str
    size: int
    attachment_id: str


class Email(BaseModel):
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
    thread_id: str
    subject: str
    emails: list[Email]
    participants: list[EmailAddress]
    last_message_date: datetime
    unread_count: int = 0


class EmailListResponse(BaseModel):
    emails: list[Email]
    total: int
    page: int
    page_size: int
