"""Config par domaine : chaque module importe ce dont il a besoin."""
# Ré-export des classes
from backend.config.Settings.authSettings import AuthSettings
from backend.config.Settings.storageSettings import StorageSettings
from backend.config.Settings.emailSettings import EmailSettings
from backend.config.Settings.apiSettings import ApiSettings

# Ré-export des instances (créées dans settingsLoader)
from backend.config.Settings.settingsLoader import (
    auth_settings,
    storage_settings,
    email_settings,
    api_settings,
)

__all__ = [
    "auth_settings",
    "storage_settings",
    "email_settings",
    "api_settings",
    "AuthSettings",
    "StorageSettings",
    "EmailSettings",
    "ApiSettings",
]
