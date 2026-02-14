# pylint: disable=invalid-name
"""Modèle Pydantic : header d'un message Gmail."""
from pydantic import BaseModel


class GmailHeader(BaseModel):
    """Header individuel d'un message Gmail."""

    name: str
    value: str
