# pylint: disable=invalid-name
"""Modèle Pydantic : payload d'un message Gmail."""
from pydantic import BaseModel, Field

from backend.core.models.Gmail.gmailHeader import GmailHeader
from backend.core.models.Gmail.gmailPart import GmailPart


class GmailPayload(BaseModel):
    """Payload normalisé d'un message Gmail."""

    headers: list[GmailHeader] = Field(default_factory=list)
    parts: list[GmailPart] = Field(default_factory=list)
