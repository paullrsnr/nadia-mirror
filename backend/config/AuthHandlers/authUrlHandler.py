# pylint: disable=invalid-name
"""Enum : handler de génération d'URL d'authentification par provider."""
from enum import Enum
from typing import Callable

from backend.config.providers import EmailProvider


class AuthUrlHandler(Enum):
    """Enum : provider → générateur d'URL d'auth."""

    GMAIL = "gmail"  # Valeurs distinctes pour éviter les alias
    OUTLOOK = "outlook"

    def __init__(self, provider_value: str):
        # Les attributs seront ajoutés dynamiquement par register()
        pass

    @classmethod
    def get_handler(cls, provider: str) -> Callable[[str], str] | None:
        """Retourne le handler pour un provider donné."""
        # Enregistrement lazy pour éviter les imports circulaires
        cls._ensure_registered()
        
        for member in cls:
            if hasattr(member, 'provider_value') and member.provider_value == provider:
                return member.handler
        return None
    
    @classmethod
    def _ensure_registered(cls):
        """S'assure que les handlers sont enregistrés (lazy loading)."""
        if not hasattr(cls, '_registered'):
            from backend.config.AuthHandlers.registry import register_all_handlers
            register_all_handlers()
            cls._registered = True

    @classmethod
    def register(cls, provider_value: str, handler: Callable[[str], str]):
        """Enregistre un handler pour un provider."""
        for member in cls:
            if member.name == provider_value.upper():
                member.provider_value = provider_value
                member.handler = handler
                break
