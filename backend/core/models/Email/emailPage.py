from dataclasses import dataclass
from typing import Optional

from backend.core.models.Email.email import Email


@dataclass
class EmailPage:
    emails: list[Email]
    next_page_token: Optional[str] = None
