# pylint: disable=invalid-name
"""Modèle métier pour un modèle LLM installé localement."""
from dataclasses import dataclass


@dataclass
class InstalledModel:
    """Modèle LLM installé localement dans resources/."""
    id: str
    name: str
    path: str
