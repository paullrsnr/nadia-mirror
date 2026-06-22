from backend.core.models.auth import AuthIdentity, AuthUrl
from backend.core.models.email import EmailListResult
from backend.core.models.email import (
    ArchiveResult,
    StarResult,
    MarkReadResult,
    SyncResult,
    SyncAllResult,
    ProviderSyncResult,
)

AuthUrlResponse = AuthUrl
AuthStatusResponse = AuthIdentity
EmailListResponse = EmailListResult
ArchiveEmailResponse = ArchiveResult
StarEmailResponse = StarResult
MarkReadResponse = MarkReadResult
SyncEmailsResponse = SyncResult | SyncAllResult
SyncEmailsProviderResponse = ProviderSyncResult
