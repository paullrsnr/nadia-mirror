# pylint: disable=invalid-name
"""Modèles métier du domaine authentification (core)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthUrl:
    """Représentation métier d'une URL d'authentification OAuth."""

    auth_url: str


@dataclass
class AuthStatus:
    """Représentation métier du statut d'authentification d'un utilisateur."""

    is_authenticated: bool
    email: Optional[str] = None
