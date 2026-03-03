"""Modèle : message Microsoft Graph complet (API response)."""
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from backend.adapters.MailProvider.Outlook.models.graphRecipient import GraphRecipient
from backend.adapters.MailProvider.Outlook.models.graphMessageBody import GraphMessageBody


class GraphMessage(BaseModel):
    id: str = ""
    conversation_id: str = Field(default="", alias="conversationId")
    subject: str = ""
    from_: Optional[GraphRecipient] = Field(default=None, alias="from")
    to_recipients: list[GraphRecipient] = Field(default_factory=list, alias="toRecipients")
    body: Optional[GraphMessageBody] = None
    body_preview: Optional[str] = Field(default=None, alias="bodyPreview")
    received_date_time: Optional[str] = Field(default=None, alias="receivedDateTime")

    model_config = ConfigDict(extra="ignore", populate_by_name=True)
