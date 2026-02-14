# pylint: disable=invalid-name
"""
Point d'entrée de compatibilité : ré-exporte depuis Gmail/.

Les nouveaux imports doivent utiliser :
    from backend.core.models.Gmail import GmailMessage
"""
from backend.core.models.Gmail import (
    GmailBody,
    GmailPart,
    GmailHeader,
    GmailPayload,
    GmailMessage,
)

__all__ = [
    "GmailBody",
    "GmailPart",
    "GmailHeader",
    "GmailPayload",
    "GmailMessage",
]
