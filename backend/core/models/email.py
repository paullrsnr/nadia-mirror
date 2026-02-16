# pylint: disable=invalid-name
"""
Point d'entrée de compatibilité : ré-exporte depuis Email/.

Les nouveaux imports doivent utiliser :
    from backend.core.models.Email import Email, EmailAddress, etc.
"""
from backend.core.models.Email import (
    EmailListQuery,
    EmailAddress,
    EmailAttachment,
    Email,
    EmailThread,
    EmailListResult,
    EmailPage,
    EmailProvider,
)

__all__ = [
    "EmailListQuery",
    "EmailAddress",
    "EmailAttachment",
    "Email",
    "EmailThread",
    "EmailListResult",
    "EmailPage",
    "EmailProvider",
]
