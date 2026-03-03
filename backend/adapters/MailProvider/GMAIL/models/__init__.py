"""Modèles bruts de l'API Gmail (JSON responses)."""
from backend.adapters.MailProvider.GMAIL.models.gmailBody import GmailBody
from backend.adapters.MailProvider.GMAIL.models.gmailHeader import GmailHeader
from backend.adapters.MailProvider.GMAIL.models.gmailPart import GmailPart
from backend.adapters.MailProvider.GMAIL.models.gmailPayload import GmailPayload
from backend.adapters.MailProvider.GMAIL.models.gmailMessage import GmailMessage
from backend.adapters.MailProvider.GMAIL.models.gmailBodyData import GmailBodyData
from backend.adapters.MailProvider.GMAIL.models.gmailPartForBody import GmailPartForBody

__all__ = [
    "GmailBody", "GmailHeader", "GmailPart", "GmailPayload",
    "GmailMessage", "GmailBodyData", "GmailPartForBody",
]
