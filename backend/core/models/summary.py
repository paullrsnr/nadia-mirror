from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EmailSummary(BaseModel):
    """Résumé d'un email"""
    email_id: str
    summary: str
    key_subject: str
    important_elements: dict
    tone: str
    importance_score: int
    importance_level: str
    created_at: datetime
    updated_at: datetime
