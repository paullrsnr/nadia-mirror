from dataclasses import dataclass, field


@dataclass
class SummarizeRequest:
    subject: str
    body: str
    from_address: str = field(default="")
