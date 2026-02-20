# pylint: disable=invalid-name
"""Modèle métier pour le statut du service LLM."""
from dataclasses import dataclass
from typing import Optional

from backend.core.models.llm.installedModel import InstalledModel  # noqa: E402


@dataclass
class LLMStatus:
    """Statut détaillé du service LLM."""
    available: bool
    message: str
    resources_path: str
    resolved_model_path: Optional[str]
    resolved_model_exists: Optional[bool]
    selected_model_id: Optional[str]
    installed_models: list[InstalledModel]
