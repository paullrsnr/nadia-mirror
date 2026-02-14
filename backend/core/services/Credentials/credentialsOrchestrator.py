# pylint: disable=invalid-name
"""Orchestrateur de credentials : dispatche les opérations vers le bon service provider."""
from google.oauth2.credentials import Credentials

from backend.config.CredentialsHandlers import (
    SaveCredentialsHandler,
    LoadCredentialsHandler,
    ClearCredentialsHandler,
)
from backend.core.models.Auth import OutlookTokens


def save_credentials(credentials: Credentials | OutlookTokens, provider: str) -> None:
    """Sauvegarde les credentials pour le provider (Gmail: Credentials, Outlook: OutlookTokens)."""
    resolved = provider.lower()
    handler_info = SaveCredentialsHandler.get_handler(resolved)
    if not handler_info:
        raise ValueError(f"Provider credentials non supporté: {resolved}")
    
    if not isinstance(credentials, handler_info.expected_type):
        raise TypeError(handler_info.error_msg)
    
    handler_info.save_func(credentials)


def load_credentials(provider: str) -> Credentials | OutlookTokens | None:
    """Charge les credentials pour le provider (Gmail: Credentials, Outlook: OutlookTokens)."""
    resolved = provider.lower()
    handler = LoadCredentialsHandler.get_handler(resolved)
    if not handler:
        raise ValueError(f"Provider credentials non supporté: {resolved}")
    return handler()


def clear_credentials(provider: str) -> None:
    """Supprime les credentials pour le provider."""
    resolved = provider.lower()
    handler = ClearCredentialsHandler.get_handler(resolved)
    if not handler:
        raise ValueError(f"Provider credentials non supporté: {resolved}")
    handler()
