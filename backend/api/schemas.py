"""Schémas Pydantic pour l'API (DTOs de réponse/requête)."""
from backend.core.models.auth import AuthIdentity, AuthUrl
from backend.core.models.email import EmailListResult

# Réutilisation des modèles métier pour les réponses API
AuthUrlResponse = AuthUrl
AuthStatusResponse = AuthIdentity
EmailListResponse = EmailListResult
