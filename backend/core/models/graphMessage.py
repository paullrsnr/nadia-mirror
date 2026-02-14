# pylint: disable=invalid-name
"""
Point d'entrée de compatibilité : ré-exporte depuis Graph/.

Les nouveaux imports doivent utiliser :
    from backend.core.models.Graph import GraphMessage, GraphRecipient
"""
from backend.core.models.Graph import (
    GraphEmailAddress,
    GraphRecipient,
    GraphMessageBody,
    GraphMessage,
)

__all__ = [
    "GraphEmailAddress",
    "GraphRecipient",
    "GraphMessageBody",
    "GraphMessage",
]
