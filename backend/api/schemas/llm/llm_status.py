# pylint: disable=invalid-name
"""Schéma API pour le statut du service LLM."""
from pydantic import BaseModel

from backend.api.schemas.llm.installed_model import InstalledModelResponse


class LLMStatusResponse(BaseModel):
    """Réponse pour l'endpoint status LLM."""
    available: bool
    message: str
    resolved_model_path: str | None = None
    resolved_model_exists: bool | None = None
    resources_path: str | None = None
    selected_model_id: str | None = None
    installed_models: list[InstalledModelResponse]
