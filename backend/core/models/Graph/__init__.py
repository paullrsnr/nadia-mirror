"""Modèles Pydantic pour le JSON renvoyé par l'API Microsoft Graph."""
from backend.core.models.Graph.graphEmailAddress import GraphEmailAddress
from backend.core.models.Graph.graphRecipient import GraphRecipient
from backend.core.models.Graph.graphMessageBody import GraphMessageBody
from backend.core.models.Graph.graphMessage import GraphMessage

__all__ = [
    "GraphEmailAddress",
    "GraphRecipient",
    "GraphMessageBody",
    "GraphMessage",
]
