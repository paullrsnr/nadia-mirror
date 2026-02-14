# pylint: disable=invalid-name
"""Modèle Pydantic : destinataire Microsoft Graph."""
from pydantic import BaseModel, Field, ConfigDict

from backend.core.models.Graph.graphEmailAddress import GraphEmailAddress


class GraphRecipient(BaseModel):
    """Destinataire Graph (from ou élément de toRecipients)."""

    email_address: GraphEmailAddress = Field(alias="emailAddress")

    model_config = ConfigDict(populate_by_name=True)
