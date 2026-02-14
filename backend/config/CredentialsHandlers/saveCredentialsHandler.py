# pylint: disable=invalid-name
"""Enum : handler de sauvegarde des credentials par provider."""
from enum import Enum
from typing import Callable, Type

from backend.config.providers import EmailProvider


class SaveCredentialsHandler(Enum):
    """Enum : provider → handler de sauvegarde des credentials."""

    GMAIL = "gmail"  # Valeurs distinctes pour éviter les alias
    OUTLOOK = "outlook"

    def __init__(self, provider_value: str):
        # Les attributs seront ajoutés dynamiquement par register()
        pass

    @classmethod
    def get_handler(cls, provider: str):
        """Retourne les infos de handler pour un provider donné."""
        # Enregistrement lazy pour éviter les imports circulaires
        cls._ensure_registered()
        
        for member in cls:
            if hasattr(member, 'provider_value') and member.provider_value == provider:
                return member
        return None
    
    @classmethod
    def _ensure_registered(cls):
        """S'assure que les handlers sont enregistrés (lazy loading)."""
        if not hasattr(cls, '_registered'):
            from backend.config.CredentialsHandlers.registry import register_all_handlers
            register_all_handlers()
            cls._registered = True

    @classmethod
    def register(cls, provider_value: str, save_func: Callable, expected_type: Type, error_msg: str):
        """Enregistre un handler pour un provider (appelé à l'initialisation du module)."""
        for member in cls:
            if member.name == provider_value.upper():
                member.provider_value = provider_value
                member.save_func = save_func
                member.expected_type = expected_type
                member.error_msg = error_msg
                break
