"""Schémas Pydantic pour l'API (DTOs de réponse/requête)."""
from backend.core.models.auth import AuthStatus, AuthUrl
from backend.core.models.email import EmailListResult

# Réutilisation des modèles métier pour les réponses API
AuthUrlResponse = AuthUrl
AuthStatusResponse = AuthStatus
EmailListResponse = EmailListResult


# AuthCallbackRequest - À implémenter
