from dataclasses import dataclass


@dataclass
class ThreadMessageItem:
    from_address: str
    body: str
    date: str = ""
