# pylint: disable=invalid-name
"""Constantes et enums pour les providers d'email (Gmail, Outlook, etc.).

Point central pour éviter les doublons de chaînes littérales.
"""
from enum import Enum


class EmailProvider(str, Enum):
    """Providers d'email supportés."""

    GMAIL = "gmail"
    OUTLOOK = "outlook"
    ALL = "all"  # Pseudo-provider pour "toutes les boîtes"


# --- Tuples de validation (utilisés pour membership tests) ---

# Providers connectables (excluant "all")
CONNECTABLE_PROVIDERS = (EmailProvider.GMAIL.value, EmailProvider.OUTLOOK.value)

# Providers valides pour liste/sync (incluant "all")
LIST_PROVIDERS = (EmailProvider.GMAIL.value, EmailProvider.OUTLOOK.value, EmailProvider.ALL.value)


# --- Valeurs par défaut ---

DEFAULT_PROVIDER = EmailProvider.GMAIL.value


# --- Messages d'erreur standards ---

MSG_UNAUTHENTICATED = "Non authentifié"
MSG_INVALID_PROVIDER = "Provider invalide"
MSG_PROVIDER_REQUIRED = "Provider requis (gmail ou outlook)"
