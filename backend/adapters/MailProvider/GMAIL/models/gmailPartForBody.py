"""Modèle de parsing : part Gmail pour l'extraction du corps (structure récursive)."""
from dataclasses import dataclass, field

from backend.adapters.MailProvider.GMAIL.models.gmailBodyData import GmailBodyData


@dataclass
class GmailPartForBody:
    mime_type: str = ""
    body: GmailBodyData = field(default_factory=GmailBodyData)
    parts: list["GmailPartForBody"] = field(default_factory=list)
