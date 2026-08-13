from dataclasses import dataclass


@dataclass
class AttachmentContent:
    filename: str
    mime_type: str
    content: bytes
