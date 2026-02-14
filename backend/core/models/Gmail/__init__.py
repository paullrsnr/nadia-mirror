"""Modèles Pydantic pour le JSON renvoyé par l'API Gmail."""
from backend.core.models.Gmail.gmailBody import GmailBody
from backend.core.models.Gmail.gmailPart import GmailPart
from backend.core.models.Gmail.gmailHeader import GmailHeader
from backend.core.models.Gmail.gmailPayload import GmailPayload
from backend.core.models.Gmail.gmailMessage import GmailMessage
from backend.core.models.Gmail.parsing import GmailBodyData, GmailPartForBody

__all__ = [
    "GmailBody",
    "GmailPart",
    "GmailHeader",
    "GmailPayload",
    "GmailMessage",
    "GmailBodyData",
    "GmailPartForBody",
]
