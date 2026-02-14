# pylint: disable=invalid-name
"""Modèle Pydantic : message Microsoft Graph complet."""
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from backend.core.models.Graph.graphRecipient import GraphRecipient
from backend.core.models.Graph.graphMessageBody import GraphMessageBody


class GraphMessage(BaseModel):
    """Message Microsoft Graph typé, correspondant au JSON renvoyé par l'API."""

    id: str = ""
    conversation_id: str = Field(default="", alias="conversationId")
    subject: str = ""
    from_: Optional[GraphRecipient] = Field(default=None, alias="from")
    to_recipients: list[GraphRecipient] = Field(
        default_factory=list, alias="toRecipients"
    )
    body: Optional[GraphMessageBody] = None
    body_preview: Optional[str] = Field(default=None, alias="bodyPreview")
    received_date_time: Optional[str] = Field(
        default=None, alias="receivedDateTime"
    )

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )
