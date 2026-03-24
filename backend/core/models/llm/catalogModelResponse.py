from dataclasses import dataclass

@dataclass
class CatalogModelResponse:
    id: str
    name: str
    repo: str
    filename: str
    description: str
    category: str
