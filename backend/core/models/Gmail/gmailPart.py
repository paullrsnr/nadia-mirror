# pylint: disable=invalid-name
"""Modèle Pydantic : part du payload Gmail."""
from pydantic import BaseModel, Field

from backend.core.models.Gmail.gmailBody import GmailBody


class GmailPart(BaseModel):
    """Représentation typée d'une part du payload Gmail."""

    filename: str = ""
    mime_type: str = Field(
        default="application/octet-stream",
        alias="mimeType",
    )
    body: GmailBody
