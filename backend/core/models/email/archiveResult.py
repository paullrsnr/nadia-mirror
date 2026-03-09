from typing import Literal
from pydantic import BaseModel


class ArchiveResult(BaseModel):
    status: Literal["success", "error"]
    email_id: str
