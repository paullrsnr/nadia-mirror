from typing import Literal
from dataclasses import dataclass


@dataclass
class StarResult:
    status: Literal["success", "error"]
    email_id: str
    is_starred: bool
