# pylint: disable=invalid-name
"""Schéma API pour un modèle installé."""
from pydantic import BaseModel


class InstalledModelResponse(BaseModel):
    """Modèle installé pour l'API."""
    id: str
    name: str
    path: str
