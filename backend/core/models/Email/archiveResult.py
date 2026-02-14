# pylint: disable=invalid-name
"""Modèle métier : résultat d'archivage d'un email."""
from typing import Literal
from pydantic import BaseModel


class ArchiveResult(BaseModel):
    """Résultat de l'archivage d'un email."""

    status: Literal["success", "error"]
    email_id: str
