from typing import Literal
from dataclasses import dataclass


@dataclass
class ArchiveResult:
    status: Literal["success", "error"]
    email_id: str
