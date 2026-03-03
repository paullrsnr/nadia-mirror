"""Modèle : header d'un message Gmail (API response)."""
from pydantic import BaseModel


class GmailHeader(BaseModel):
    name: str
    value: str
