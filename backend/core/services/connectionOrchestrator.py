# pylint: disable=invalid-name
"""Orchestrateur de connexion : point d'entrée unique pour les credentials par provider.

Délègue au credentialsService (Gmail, Outlook).
"""
from google.oauth2.credentials import Credentials

from backend.config.settings import email_settings
from backend.core.services import credentialsService

# Gmail renvoie Credentials, Outlook renvoie un dict de tokens
ConnectionCredentials = Credentials | dict


def _resolve_provider(provider: str | None) -> str:
    """Provider effectif (paramètre ou défaut config)."""
    return (provider or email_settings.DEFAULT_PROVIDER).lower()


def get_connection_credentials(
    provider: str | None = None,
) -> ConnectionCredentials | None:
    """Charge les credentials de connexion pour le provider (défaut = config)."""
    resolved_provider = _resolve_provider(provider)
    return credentialsService.load_credentials(resolved_provider)


def save_connection_credentials(
    credentials: ConnectionCredentials,
    provider: str | None = None,
) -> None:
    """Sauvegarde les credentials de connexion pour le provider (défaut = config)."""
    resolved_provider = _resolve_provider(provider)
    credentialsService.save_credentials(credentials, resolved_provider)


def clear_connection_credentials(provider: str | None = None) -> None:
    """Supprime les credentials de connexion pour le provider (déconnexion)."""
    resolved_provider = _resolve_provider(provider)
    credentialsService.clear_credentials(resolved_provider)
