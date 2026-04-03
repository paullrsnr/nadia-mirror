from typing import Optional
from pydantic import BaseModel


class SuggestReplyResult(BaseModel):
    important: bool
    draft: Optional[str]
