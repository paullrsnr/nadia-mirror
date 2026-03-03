"""Modèle : message Gmail complet (API response)."""
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from backend.adapters.MailProvider.GMAIL.models.gmailPayload import GmailPayload


class GmailMessage(BaseModel):
    id: str
    thread_id: str = Field(alias="threadId")
    payload: GmailPayload
    label_ids: list[str] = Field(default_factory=list, alias="labelIds")
    snippet: Optional[str] = None

    model_config = ConfigDict(extra="ignore", populate_by_name=True)
