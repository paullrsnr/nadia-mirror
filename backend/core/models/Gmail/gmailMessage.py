# pylint: disable=invalid-name
"""Modèle Pydantic : message Gmail complet."""
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from backend.core.models.Gmail.gmailPayload import GmailPayload


class GmailMessage(BaseModel):
    """Message Gmail typé, correspondant au JSON renvoyé par l'API Gmail."""

    id: str
    thread_id: str = Field(alias="threadId")
    payload: GmailPayload
    label_ids: list[str] = Field(default_factory=list, alias="labelIds")
    snippet: Optional[str] = None

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )
