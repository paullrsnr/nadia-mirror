"""Schémas Pydantic pour l'API (DTOs de réponse/requête)."""
from backend.core.models.Auth import AuthIdentity, AuthUrl
from backend.core.models.Email import EmailListResult
from backend.core.models.Email import (
    ArchiveResult,
    SyncResult,
    SyncAllResult,
    ProviderSyncResult,
)

# Réutilisation des modèles métier pour les réponses API
AuthUrlResponse = AuthUrl
AuthStatusResponse = AuthIdentity
EmailListResponse = EmailListResult
ArchiveEmailResponse = ArchiveResult
SyncEmailsResponse = SyncResult | SyncAllResult
SyncEmailsProviderResponse = ProviderSyncResult
