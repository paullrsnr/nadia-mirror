# pylint: disable=invalid-name
"""Schéma API pour le chargement d'un modèle."""
from pydantic import BaseModel


class LoadModelRequest(BaseModel):
    """Requête pour charger un modèle (par id ou nom de fichier)."""
    model_id: str
