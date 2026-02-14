# pylint: disable=invalid-name
"""
Point d'entrée de compatibilité : ré-exporte depuis Auth/.

Les nouveaux imports doivent utiliser :
    from backend.core.models.Auth import AuthUrl, AuthIdentity
"""
from backend.core.models.Auth import AuthUrl, AuthIdentity

__all__ = [
    "AuthUrl",
    "AuthIdentity",
]
