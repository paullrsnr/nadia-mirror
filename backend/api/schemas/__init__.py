"""Schémas Pydantic pour l'API (DTOs de réponse/requête)."""
from backend.core.models.auth import AuthIdentity, AuthUrl
from backend.core.models.email import EmailListResult
from backend.core.models.Email import (
    ArchiveResult,
    SyncResult,
    SyncAllResult,
    ProviderSyncResult,
)

from backend.api.schemas.llm import (
    InstalledModelResponse,
    CatalogModelResponse,
    LLMStatusResponse,
    DownloadModelRequest,
    LoadModelRequest,
)

# Réutilisation des modèles métier pour les réponses API
AuthUrlResponse = AuthUrl
AuthStatusResponse = AuthIdentity
EmailListResponse = EmailListResult
ArchiveEmailResponse = ArchiveResult
SyncEmailsResponse = SyncResult | SyncAllResult
SyncEmailsProviderResponse = ProviderSyncResult

__all__ = [
    "AuthUrlResponse",
    "AuthStatusResponse",
    "EmailListResponse",
    "ArchiveEmailResponse",
    "SyncEmailsResponse",
    "SyncEmailsProviderResponse",
    "InstalledModelResponse",
    "CatalogModelResponse",
    "LLMStatusResponse",
    "DownloadModelRequest",
    "LoadModelRequest",
]
