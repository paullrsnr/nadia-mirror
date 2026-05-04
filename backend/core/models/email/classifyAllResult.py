from dataclasses import dataclass, field

from backend.core.models.email.classifyResult import ClassifyResult


@dataclass
class ClassifyAllResult:
    classified: int
    results: list[ClassifyResult] = field(default_factory=list)
