# pylint: disable=invalid-name
"""Orchestrateur de connexion : point d'entrée unique pour les credentials par provider.

Délègue au credentialsOrchestrator (Gmail, Outlook).
"""
from google.oauth2.credentials import Credentials

from backend.config.settings import email_settings
from backend.core.services.Credentials.credentialsOrchestrator import (
    load_credentials,
    save_credentials,
    clear_credentials,
)
from backend.core.models.Auth import OutlookTokens

# Gmail renvoie Credentials, Outlook renvoie OutlookTokens
ConnectionCredentials = Credentials | OutlookTokens


def _resolve_provider(provider: str | None) -> str:
    """Provider effectif (paramètre ou défaut config)."""
    return (provider or email_settings.DEFAULT_PROVIDER).lower()


def get_connection_credentials(
    provider: str | None = None,
) -> ConnectionCredentials | None:
    """Charge les credentials de connexion pour le provider (défaut = config)."""
    resolved_provider = _resolve_provider(provider)
    return load_credentials(resolved_provider)


def save_connection_credentials(
    credentials: ConnectionCredentials,
    provider: str | None = None,
) -> None:
    """Sauvegarde les credentials de connexion pour le provider (défaut = config)."""
    resolved_provider = _resolve_provider(provider)
    save_credentials(credentials, resolved_provider)


def clear_connection_credentials(provider: str | None = None) -> None:
    """Supprime les credentials de connexion pour le provider (déconnexion)."""
    resolved_provider = _resolve_provider(provider)
    clear_credentials(resolved_provider)
