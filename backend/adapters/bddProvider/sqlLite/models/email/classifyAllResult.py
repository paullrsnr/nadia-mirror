from pydantic import BaseModel

from backend.adapters.bddProvider.sqlLite.models.email.classifyResult import ClassifyResult


class ClassifyAllResult(BaseModel):
    classified: int
    results: list[ClassifyResult]
