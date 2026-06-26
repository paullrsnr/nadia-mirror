"""Exceptions métier du domaine — aucune dépendance à un framework."""


class AuthError(Exception):
    """credentials manquants ou invalides pour un provider."""


class ProviderError(Exception):
    """Provider invalide ou non supporté."""


class NotFoundError(Exception):
    """Ressource introuvable."""


class ValidationError(Exception):
    """Entrée utilisateur invalide."""
