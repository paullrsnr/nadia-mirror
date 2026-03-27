from dataclasses import dataclass


@dataclass
class InstalledModelResponse:
    id: str
    name: str
    path: str
