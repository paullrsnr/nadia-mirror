from dataclasses import dataclass


@dataclass
class ClassifyEmailRequest:
    subject: str
    snippet: str = ""
    from_address: str = ""
