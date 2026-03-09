from typing import Optional
from pydantic import BaseModel


class EmailAddress(BaseModel):
    email: str
    name: Optional[str] = None
