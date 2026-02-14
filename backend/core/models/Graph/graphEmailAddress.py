# pylint: disable=invalid-name
"""Modèle Pydantic : emailAddress Microsoft Graph."""
from typing import Optional

from pydantic import BaseModel


class GraphEmailAddress(BaseModel):
    """Représentation typée de emailAddress dans Graph (from, toRecipients)."""

    name: Optional[str] = None
    address: str = ""
