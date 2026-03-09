from enum import Enum


class Provider(str, Enum):
    """Identifiant d'un provider d'email."""

    GMAIL = "gmail"
    OUTLOOK = "outlook"
    ALL = "all"  # Pseudo-provider : toutes les boîtes
