# pylint: disable=invalid-name
"""Enum : handler de suppression des credentials par provider."""
from enum import Enum
from typing import Callable


class ClearCredentialsHandler(Enum):
    """Enum : provider → handler de suppression des credentials."""

    GMAIL = "gmail"  # Valeurs distinctes pour éviter les alias
    OUTLOOK = "outlook"

    def __init__(self, provider_value: str):
        # Les attributs seront ajoutés dynamiquement par register()
        pass

    @classmethod
    def get_handler(cls, provider: str) -> Callable | None:
        """Retourne le handler pour un provider donné."""
        # Enregistrement lazy pour éviter les imports circulaires
        cls._ensure_registered()

        for member in cls:
            if hasattr(member, 'provider_value') and member.provider_value == provider:
                return member.clear_func
        return None

    @classmethod
    def _ensure_registered(cls):
        """S'assure que les handlers sont enregistrés (lazy loading)."""
        if not hasattr(cls, '_registered'):
            from backend.config.CredentialsHandlers.registry import register_all_handlers
            register_all_handlers()
            cls._registered = True

    @classmethod
    def register(cls, provider_value: str, clear_func: Callable):
        """Enregistre un handler pour un provider (appelé à l'initialisation du module)."""
        for member in cls:
            if member.name == provider_value.upper():
                member.provider_value = provider_value
                member.clear_func = clear_func
                break
