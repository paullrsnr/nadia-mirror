from typing import Literal
from dataclasses import dataclass


@dataclass
class MarkReadResult:
    status: Literal["success", "error"]
    email_id: str
