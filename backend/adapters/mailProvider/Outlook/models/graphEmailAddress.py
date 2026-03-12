from typing import Optional

from pydantic import BaseModel


class GraphEmailAddress(BaseModel):
    name: Optional[str] = None
    address: str = ""
