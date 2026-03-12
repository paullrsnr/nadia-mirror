from pydantic import BaseModel, Field

from backend.adapters.mailProvider.GMAIL.models.gmailBody import GmailBody


class GmailPart(BaseModel):
    filename: str = ""
    mime_type: str = Field(default="application/octet-stream", alias="mimeType")
    body: GmailBody
