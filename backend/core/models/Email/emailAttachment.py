# pylint: disable=invalid-name
"""Modèle métier : pièce jointe d'un email."""
from typing import Optional
from pydantic import BaseModel


class EmailAttachment(BaseModel):
    """Représentation métier d'une pièce jointe d'email."""

    filename: str
    mime_type: str
    size: int
    attachment_id: Optional[str] = None  # ID pour télécharger depuis Gmail/Outlook
