from pydantic import BaseModel
from typing import Optional


class EmailClassification(BaseModel):
    """Classification d'un email"""
    email_id: str
    category: str  # travail, personnel, spam, etc.
    priority: str  # haute, moyenne, faible
    requires_action: bool
    estimated_read_time: int  # en secondes
    tags: list[str] = []
