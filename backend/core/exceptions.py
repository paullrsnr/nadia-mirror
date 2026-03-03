"""Exceptions métier du domaine — aucune dépendance à un framework."""


class AuthError(Exception):
    """Credentials manquants ou invalides pour un provider."""


class ProviderError(Exception):
    """Provider invalide ou non supporté."""
