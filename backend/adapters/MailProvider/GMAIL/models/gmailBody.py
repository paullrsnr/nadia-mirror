"""Modèle : partie 'body' d'un message Gmail (API response)."""
from typing import Optional

from pydantic import BaseModel, Field


class GmailBody(BaseModel):
    size: int = 0
    attachment_id: Optional[str] = Field(default=None, alias="attachmentId")
