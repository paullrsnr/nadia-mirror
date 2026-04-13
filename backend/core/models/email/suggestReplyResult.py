from dataclasses import dataclass
from typing import Optional


@dataclass
class SuggestReplyResult:
    important: bool
    draft: Optional[str]
