# pylint: disable=invalid-name
"""Schéma API pour un modèle du catalogue."""
from pydantic import BaseModel


class CatalogModelResponse(BaseModel):
    """Modèle du catalogue pour l'API."""
    id: str
    name: str
    repo: str
    filename: str
    description: str
    category: str
