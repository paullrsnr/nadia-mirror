from dataclasses import dataclass, field
from typing import List

from backend.core.models.llm.threadMessageItem import ThreadMessageItem


@dataclass
class SummarizeThreadRequest:
    subject: str
    messages: List[ThreadMessageItem] = field(default_factory=list)
