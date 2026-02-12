# pylint: disable=invalid-name
"""Modèles métier du domaine authentification (core)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthUrl:
    """Représentation métier d'une URL d'authentification OAuth."""

    auth_url: str


@dataclass
class AuthIdentity:
    """Représentation métier de l'identité d'un utilisateur authentifié (ou non)."""

    is_authenticated: bool
    email: Optional[str] = None
