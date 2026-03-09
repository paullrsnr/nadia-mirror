from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthIdentity:

    is_authenticated: bool
    email: Optional[str] = None
