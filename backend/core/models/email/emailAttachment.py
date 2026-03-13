from typing import Optional
from dataclasses import dataclass


@dataclass
class EmailAttachment:
    filename: str
    mime_type: str
    size: int
    attachment_id: Optional[str] = None
