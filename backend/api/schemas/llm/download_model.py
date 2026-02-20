# pylint: disable=invalid-name
"""Schéma API pour le téléchargement d'un modèle."""
from pydantic import BaseModel


class DownloadModelRequest(BaseModel):
    """Requête pour télécharger un modèle depuis le catalogue."""
    repo: str
    filename: str
