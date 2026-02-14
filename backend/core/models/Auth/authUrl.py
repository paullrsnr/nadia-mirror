# pylint: disable=invalid-name
"""Modèle métier : URL d'authentification OAuth."""
from dataclasses import dataclass


@dataclass
class AuthUrl:
    """Représentation métier d'une URL d'authentification OAuth."""

    auth_url: str
