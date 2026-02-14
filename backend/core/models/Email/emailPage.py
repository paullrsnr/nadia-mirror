# pylint: disable=invalid-name
"""Modèle métier : page d'emails retournée par un provider externe."""
from dataclasses import dataclass
from typing import Optional

from backend.core.models.Email.email import Email


@dataclass
class EmailPage:
    """Page d'emails retournée par un provider externe (ex: Gmail).

    Contient la liste d'emails et, éventuellement, un curseur de pagination
    (`next_page_token`) fourni par l'API distante (Gmail).
    """

    emails: list[Email]
    next_page_token: Optional[str] = None
