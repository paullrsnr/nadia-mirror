# pylint: disable=invalid-name
"""Modèle métier : identité d'un utilisateur authentifié."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthIdentity:
    """Représentation métier de l'identité d'un utilisateur authentifié (ou non)."""

    is_authenticated: bool
    email: Optional[str] = None
