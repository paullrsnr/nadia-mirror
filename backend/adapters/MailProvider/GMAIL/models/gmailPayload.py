from pydantic import BaseModel, Field

from backend.adapters.mailProvider.GMAIL.models.gmailHeader import GmailHeader
from backend.adapters.mailProvider.GMAIL.models.gmailPart import GmailPart


class GmailPayload(BaseModel):
    headers: list[GmailHeader] = Field(default_factory=list)
    parts: list[GmailPart] = Field(default_factory=list)
