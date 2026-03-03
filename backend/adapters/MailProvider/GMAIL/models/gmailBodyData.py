"""Modèle de parsing : données body d'une part Gmail (base64)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class GmailBodyData:
    data: Optional[str] = None
