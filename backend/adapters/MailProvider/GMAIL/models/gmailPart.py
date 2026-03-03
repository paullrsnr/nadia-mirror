"""Modèle : part du payload Gmail (API response)."""
from pydantic import BaseModel, Field

from backend.adapters.MailProvider.GMAIL.models.gmailBody import GmailBody


class GmailPart(BaseModel):
    filename: str = ""
    mime_type: str = Field(default="application/octet-stream", alias="mimeType")
    body: GmailBody
