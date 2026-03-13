from typing import Optional

from pydantic import BaseModel, Field


class GmailBody(BaseModel):
    size: int = 0
    attachment_id: Optional[str] = Field(default=None, alias="attachmentId")
