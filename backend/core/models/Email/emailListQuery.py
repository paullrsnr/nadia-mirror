from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class EmailListQuery:

    unread_only: bool = True
    after_date: Optional[date] = None
