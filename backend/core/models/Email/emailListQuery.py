# pylint: disable=invalid-name
"""Requête canonique (pierre de rosette) pour lister les emails.

Contrat unique : tous les adapters (Gmail, Outlook, …) reçoivent cette structure
et la traduisent en requête native. La vérité n'est ni Gmail ni Outlook, c'est ce modèle.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class EmailListQuery:
    """Requête canonique pour lister les emails.

    Utilisée par le port EmailProvider et traduite par chaque adapter
    en format natif (Gmail query string, Outlook $filter, etc.).
    """

    unread_only: bool = True
    after_date: Optional[date] = None
