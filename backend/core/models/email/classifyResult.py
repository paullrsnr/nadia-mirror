from dataclasses import dataclass


@dataclass
class ClassifyResult:
    email_id: str
    category: str
