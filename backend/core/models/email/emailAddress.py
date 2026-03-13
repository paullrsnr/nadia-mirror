from typing import Optional
from dataclasses import dataclass


@dataclass
class EmailAddress:
    email: str
    name: Optional[str] = None
