from typing import Optional
from pydantic import BaseModel


class EmailAttachment(BaseModel):
    filename: str
    mime_type: str
    size: int
    attachment_id: Optional[str] = None  # ID pour télécharger depuis Gmail/Outlook
