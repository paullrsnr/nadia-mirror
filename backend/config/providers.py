# pylint: disable=invalid-name
"""Constantes pour les providers d'email (Gmail, Outlook, etc.).

Point central pour validation et messages. L'enum EmailProvider est défini
dans backend.core.models.Email (ré-exporté ici pour compatibilité).
"""
from backend.core.models.Email import EmailProvider


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