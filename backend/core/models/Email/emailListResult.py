from pydantic import BaseModel

from backend.core.models.Email.email import Email


class EmailListResult(BaseModel):
    emails: list[Email]
    total: int
    page: int
    page_size: int
