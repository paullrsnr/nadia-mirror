# pylint: disable=invalid-name
"""Modèle métier : résultat paginé d'une liste d'emails."""
from pydantic import BaseModel

from backend.core.models.Email.email import Email


class EmailListResult(BaseModel):
    """Résultat métier d'une liste d'emails paginée."""

    emails: list[Email]
    total: int
    page: int
    page_size: int
