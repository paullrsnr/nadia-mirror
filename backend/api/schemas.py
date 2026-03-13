from backend.core.models.auth import AuthIdentity, AuthUrl
from backend.core.models.email import EmailListResult
from backend.core.models.email import (
    ArchiveResult,
    SyncResult,
    SyncAllResult,
    ProviderSyncResult,
)

AuthUrlResponse = AuthUrl
AuthStatusResponse = AuthIdentity
EmailListResponse = EmailListResult
ArchiveEmailResponse = ArchiveResult
SyncEmailsResponse = SyncResult | SyncAllResult
SyncEmailsProviderResponse = ProviderSyncResult
