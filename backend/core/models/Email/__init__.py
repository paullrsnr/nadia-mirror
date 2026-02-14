"""Modèles métier du domaine email (core). Pas de dépendance à Pydantic."""
from backend.core.models.Email.emailListQuery import EmailListQuery
from backend.core.models.Email.emailAddress import EmailAddress
from backend.core.models.Email.emailAttachment import EmailAttachment
from backend.core.models.Email.email import Email
from backend.core.models.Email.emailThread import EmailThread
from backend.core.models.Email.emailListResult import EmailListResult
from backend.core.models.Email.emailPage import EmailPage
from backend.core.models.Email.archiveResult import ArchiveResult
from backend.core.models.Email.Sync import SyncResult, ProviderSyncResult, SyncAllResult

__all__ = [
    "EmailListQuery",
    "EmailAddress",
    "EmailAttachment",
    "Email",
    "EmailThread",
    "EmailListResult",
    "EmailPage",
    "ArchiveResult",
    "SyncResult",
    "ProviderSyncResult",
    "SyncAllResult",
]
