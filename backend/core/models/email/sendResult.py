from typing import Literal
from dataclasses import dataclass


@dataclass
class SendResult:
    status: Literal["success", "error"]
    draft_id: str
    provider: str | None = None
