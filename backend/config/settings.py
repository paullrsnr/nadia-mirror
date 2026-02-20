"""
Point d'entrée de compatibilité : ré-exporte depuis Settings/.

Les nouveaux imports doivent utiliser :
    from backend.config.Settings import auth_settings, storage_settings, etc.

Ou directement :
    from backend.config.Settings.AuthSettings import AuthSettings
"""
# Ré-export pour compatibilité avec le code existant
from backend.config.Settings import (
    auth_settings,
    storage_settings,
    email_settings,
    api_settings,
    llm_settings,
    AuthSettings,
    StorageSettings,
    EmailSettings,
    ApiSettings,
    LLMSettings,
)

__all__ = [
    "auth_settings",
    "storage_settings",
    "email_settings",
    "api_settings",
    "llm_settings",
    "AuthSettings",
    "StorageSettings",
    "EmailSettings",
    "ApiSettings",
    "LLMSettings",
]
