# pylint: disable=invalid-name
"""Modèle Pydantic : corps d'un message Microsoft Graph."""
from pydantic import BaseModel, Field, ConfigDict


class GraphMessageBody(BaseModel):
    """Corps d'un message Graph."""

    content_type: str = Field(default="text", alias="contentType")
    content: str = ""

    model_config = ConfigDict(populate_by_name=True)
