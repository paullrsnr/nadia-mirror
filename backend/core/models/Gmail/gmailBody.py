# pylint: disable=invalid-name
"""Modèle Pydantic : partie 'body' d'un message Gmail."""
from typing import Optional

from pydantic import BaseModel, Field


class GmailBody(BaseModel):
    """Représentation typée de la partie 'body' d'une part Gmail."""

    size: int = 0
    attachment_id: Optional[str] = Field(default=None, alias="attachmentId")
