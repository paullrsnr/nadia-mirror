# pylint: disable=invalid-name
"""Modèle métier : adresse email."""
from typing import Optional
from pydantic import BaseModel


class EmailAddress(BaseModel):
    """Représentation métier d'une adresse email."""

    email: str
    name: Optional[str] = None
