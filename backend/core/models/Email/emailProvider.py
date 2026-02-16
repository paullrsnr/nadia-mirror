# pylint: disable=invalid-name
"""Provider d'email : Gmail, Outlook, ou toutes les boîtes (all)."""
from enum import Enum


class EmailProvider(str, Enum):
    """Providers d'email supportés."""

    GMAIL = "gmail"
    OUTLOOK = "outlook"
    ALL = "all"  # Pseudo-provider pour "toutes les boîtes"
