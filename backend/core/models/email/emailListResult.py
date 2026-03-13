from dataclasses import dataclass

from backend.core.models.email.email import Email


@dataclass
class EmailListResult:
    emails: list[Email]
    total: int
    page: int
    page_size: int
