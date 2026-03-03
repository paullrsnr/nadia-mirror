"""Modèle : payload d'un message Gmail (API response)."""
from pydantic import BaseModel, Field

from backend.adapters.MailProvider.GMAIL.models.gmailHeader import GmailHeader
from backend.adapters.MailProvider.GMAIL.models.gmailPart import GmailPart


class GmailPayload(BaseModel):
    headers: list[GmailHeader] = Field(default_factory=list)
    parts: list[GmailPart] = Field(default_factory=list)
